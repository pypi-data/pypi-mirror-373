#!/usr/bin/env python3
"""sr2t Nmap parser"""

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from prettytable import PrettyTable
from sr2t.shared.export import export_all
from sr2t.shared.utils import load_yaml


@dataclass
class HostPorts:
    """HostPorts dataclass."""

    addr: str
    open_tcp_ports: list
    open_udp_ports: list


def _iter_ports(host):
    """Yield each <port> element under a host."""
    yield from host.findall("ports/port")


def _port_matches(p, *, protocol, desired_state):
    """Return True if a port matches protocol and desired state."""
    if protocol and p.get("protocol") != protocol:
        return False
    for st in p.findall("state"):
        if st.get("state") == desired_state:
            return True
    return False


def _safe_text(elem, default=""):
    return (elem.text or "").strip() if elem is not None else default


def load_and_prepare_yaml(data_package, filename, column_map):
    """Load YAML file."""
    yaml_raw = load_yaml(None, data_package, filename)
    return {
        column_map[cat]: patterns
        for cat, patterns in yaml_raw.items()
        if cat in column_map
    }


class SSLMetadata:
    def __init__(self):
        self.subject_cn = ""
        self.issuer_cn = ""
        self.not_before = None
        self.not_after = None
        self.key_algo = ""
        self.key_size = None
        self.rsa_exponent = None
        self.signature_algo = ""
        self.revoked = False
        self.thumbprint = ""
        self.status = []
        self.is_self_signed = False
        self.is_wildcard = False


def _dt_utc(cert, attr_name):
    """Return datetime in UTC, supporting cryptography *_utc attrs when present."""
    utc_attr = f"{attr_name}_utc"
    if hasattr(cert, utc_attr):
        return getattr(cert, utc_attr)
    dt = getattr(cert, attr_name)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_ssl_cert_metadata(pem_data, *, crl_timeout=30, max_crls=5):
    """
    Parse PEM certificate and optionally check CRLs (HTTP/HTTPS only).
    Returns SSLMetadata instance.
    """
    meta = SSLMetadata()
    if not pem_data:
        return meta

    cert = x509.load_pem_x509_certificate(pem_data.encode())
    pubkey = cert.public_key()

    # SHA-1 thumbprint of DER-encoded certificate
    der_bytes = cert.public_bytes(encoding=serialization.Encoding.DER)
    meta.thumbprint = hashlib.sha256(der_bytes).hexdigest()

    # Subject CN & Issuer CN
    for attr in cert.subject:
        if getattr(attr.oid, "_name", "") == "commonName":
            meta.subject_cn = attr.value
            break

    if not meta.subject_cn:
        # Fallback to SAN DNSNames
        try:
            san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            dns_names = san.value.get_values_for_type(x509.DNSName)
            if dns_names:
                meta.subject_cn = dns_names[0]
        except x509.ExtensionNotFound:
            pass

    for attr in cert.issuer:
        if getattr(attr.oid, "_name", "") == "commonName":
            meta.issuer_cn = attr.value
            break

    # Validity
    meta.not_before = _dt_utc(cert, "not_valid_before")
    meta.not_after = _dt_utc(cert, "not_valid_after")

    # Public key meta
    meta.key_algo = pubkey.__class__.__name__
    meta.key_size = getattr(pubkey, "key_size", None)
    if hasattr(pubkey, "public_numbers"):
        try:
            meta.rsa_exponent = pubkey.public_numbers().e
        except Exception:
            meta.rsa_exponent = "no rsa key"

    # Signature algorithm
    try:
        meta.signature_algo = cert.signature_hash_algorithm.name
    except Exception:
        meta.signature_algo = ""

    # CRL URLs
    crl_urls = []
    try:
        crl_ext = cert.extensions.get_extension_for_class(x509.CRLDistributionPoints)
        for dp in crl_ext.value:
            for uri in dp.full_name or []:
                if isinstance(uri, x509.UniformResourceIdentifier):
                    scheme = uri.value.split(":", 1)[0].lower()
                    if scheme in ("http", "https"):
                        crl_urls.append(uri.value)
    except x509.ExtensionNotFound:
        pass

    # CRL check
    crl_check_succeeded = False
    serial_hex = format(cert.serial_number, "x").lower()

    for url in crl_urls[:max_crls]:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                continue
            # Stream + bounded read
            with requests.get(
                url, timeout=crl_timeout, stream=True, allow_redirects=True
            ) as r:
                r.raise_for_status()
                final = urlparse(r.url)
                if final.scheme not in ("http", "https"):
                    continue
                max_bytes = 2_000_000
                chunks = []
                total = 0
                for chunk in r.iter_content(8192):
                    if not chunk:
                        continue
                    chunks.append(chunk)
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError("CRL exceeds maximum allowed size")
            crl_data = b"".join(chunks)
            # Try DER first, then PEM
            try:
                crl = x509.load_der_x509_crl(crl_data)
            except ValueError:
                crl = x509.load_pem_x509_crl(crl_data)
            for revoked in crl:
                if format(revoked.serial_number, "x").lower() == serial_hex:
                    meta.revoked = True
                    break
            crl_check_succeeded = True
        except requests.RequestException:
            # network/DNS/HTTP errors -> best-effort, continue to next DP
            continue
        except ConnectionError:
            continue

    if not crl_check_succeeded and not meta.revoked:
        meta.status.append("revocation offline")

    # Derived flags
    meta.is_self_signed = meta.subject_cn == meta.issuer_cn and bool(meta.subject_cn)
    if meta.is_self_signed:
        meta.status.append("self-signed")
    if (meta.subject_cn or "").startswith("*."):
        meta.is_wildcard = True
        meta.status.append("wildcard")

    if meta.not_after and datetime.now(timezone.utc) > meta.not_after:
        meta.status.append("expired")

    # Deduplicate status
    meta.status = sorted(set(meta.status))
    return meta


def extract_host_data(host, args):
    """Gather host address and open port lists (TCP/UDP) for desired state."""
    addr_elem = host.find("address")
    if addr_elem is None or not addr_elem.get("addr"):
        return HostPorts(addr="", open_tcp_ports=[], open_udp_ports=[])

    addr = addr_elem.get("addr")
    tcp_ports = []
    udp_ports = []
    desired_state = args.nmap_state

    for p in _iter_ports(host):
        if _port_matches(p, protocol=None, desired_state=desired_state):
            portid = p.get("portid")
            if not portid:
                continue
            proto = p.get("protocol")
            if proto == "tcp":
                tcp_ports.append(portid)
            elif proto == "udp":
                udp_ports.append(portid)

    return HostPorts(addr=addr, open_tcp_ports=tcp_ports, open_udp_ports=udp_ports)


def extract_services(host, args, addr, out_rows):
    """Collect service rows: [addr, portid, proto, service_name, state]."""
    desired_state = args.nmap_state
    for p in _iter_ports(host):
        portid = p.get("portid")
        proto = p.get("protocol")
        for st in p.findall("state"):
            if st.get("state") == desired_state:
                for svc in p.findall("service"):
                    service_name = svc.get("name")
                    out_rows.append([addr, portid, proto, service_name, desired_state])


def _cipher_hashes_from(cipher_parts):
    """Extract trailing hash tokens from cipher names (TLS_*..._<HASH>).
    Normalizes '_SHA' to 'sha1' per TLS naming convention."""
    hashes = set()
    for c in cipher_parts:
        m = re.search(r"_([A-Za-z0-9]+)$", c)
        if not m:
            continue
        suf = m.group(1).lower()
        if suf == "sha":  # TLS '_SHA' means SHA-1 (not SHA-0/SHA-2)
            suf = "sha1"
        hashes.add(suf)
    return hashes


def _key_type_matches(requested, key_algo_str):
    """Return True if the YAML algorithm label matches the certificate key type."""
    r = (requested or "").lower()
    s = (key_algo_str or "").lower()
    if not r or not s:
        return False
    if r in s:
        return True
    # Friendly alias: YAML 'ecdsa' should match EllipticCurvePublicKey
    if r == "ecdsa" and ("ellipticcurve" in s or "ec" in s):
        return True
    return False


def _parse_semicolon_params(value: str) -> dict:
    """Generic parser for ; separated tokens like HSTS."""
    params = {}
    if not value:
        return params
    for part in (p.strip() for p in value.split(";")):
        if not part:
            continue
        if "=" in part:
            k, v = part.split("=", 1)
            params[k.strip().lower()] = v.strip()
        else:
            params[part.strip().lower()] = True
    return params


def _parse_csp(value: str) -> dict:
    """Parse CSP into {directive -> [tokens]}."""
    out = {}
    if not value:
        return out
    for seg in (s.strip() for s in value.split(";")):
        if not seg:
            continue
        parts = seg.split()
        d = parts[0].lower()
        toks = [t.strip() for t in parts[1:] if t.strip()]
        out[d] = toks
    return out


def _eval_value_rules(rules: dict, raw_value: str) -> bool:
    """Evaluate simple value rules: equals / one_of (case-insensitive)."""
    if not rules:
        return True
    v = (raw_value or "").strip().lower()
    if "equals" in rules:
        if v != str(rules["equals"]).strip().lower():
            return False
    if "one_of" in rules:
        allowed = [str(x).strip().lower() for x in rules.get("one_of", [])]
        if v not in allowed:
            return False
    return True


def _eval_params_rules(rules: dict, params: dict) -> bool:
    """Evaluate param rules for ; separated headers (e.g., HSTS)."""
    for key, cond in (rules or {}).items():
        k = key.strip().lower()
        val = params.get(k)
        if isinstance(cond, dict):
            if cond.get("required") and (val is None):
                return False
            if "min" in cond:
                try:
                    if int(val) < int(cond["min"]):
                        return False
                except Exception:
                    return False
            if "max" in cond:
                try:
                    if int(val) > int(cond["max"]):
                        return False
                except Exception:
                    return False
        elif isinstance(cond, bool):
            if cond and (val is None):
                return False
    return True


def _tokens_match_exact(tokens: list, allowed_value: str) -> bool:
    """Check directive tokens equal exactly the allowed string's tokens."""
    allowed_tokens = [t for t in allowed_value.strip().split() if t]
    return len(tokens) == len(allowed_tokens) and {t.lower() for t in tokens} == {
        t.lower() for t in allowed_tokens
    }


def _eval_csp_rules(rules: dict, csp_map: dict) -> bool:
    """Evaluate CSP 'directives' rules: deny_any / require_any / one_of."""
    for dname, drule in (rules or {}).items():
        toks = csp_map.get(dname.lower())
        if toks is None:  # directive missing
            return False
        tset = {t.lower() for t in toks}
        # deny_any: fail if any forbidden token appears
        for bad in drule.get("deny_any") or []:
            if str(bad).lower() in tset:
                return False
        # require_any: at least one required token present
        req_any = drule.get("require_any")
        if req_any and not any(str(x).lower() in tset for x in req_any):
            return False
        # one_of: directive's entire value equals one of allowed values
        one_of = drule.get("one_of")
        if one_of:
            if not any(_tokens_match_exact(toks, str(av)) for av in one_of):
                return False
    return True


def _match_flags(extracted_by_category, yaml_cfg):
    """Convert (category -> content) + YAML patterns into ["X" | ""] flags."""
    flags = []
    for category, patterns in yaml_cfg.items():
        raw_content = (extracted_by_category.get(category) or "").lower()
        content_parts = [c.strip() for c in raw_content.split(",") if c.strip()]
        if category in ("headers", "http_headers", "https_headers"):
            header_names = set(content_parts)  # names only
            is_https = extracted_by_category.get("is_https", "").lower() in (
                "1",
                "true",
                "yes",
                "y",
            )
            headers_kv = (
                extracted_by_category.get("headers_dict") or {}
            )  # name -> value

            # Normalize patterns: allow list (strings and/or dict items) or dict
            raw_patterns = yaml_cfg.get(category)
            if isinstance(raw_patterns, dict):
                # mapping {header: rules} -> list of one-key dicts
                pat_iterable = [{k: v} for k, v in raw_patterns.items()]
            else:
                pat_iterable = list(raw_patterns or [])

            for item in pat_iterable:
                # --- Case A: presence-only token (string) ---
                if isinstance(item, str):
                    p = item.strip().lower()
                    if p == "https_redir":
                        flags.append("X" if not is_https else "")
                    else:
                        if category == "https_headers" and not is_https:
                            flags.append("")  # https-only gating
                        else:
                            flags.append("X" if p not in header_names else "")
                    continue

                # --- Case B: rule-based entry: {header-name: rules} ---
                if isinstance(item, dict) and item:
                    hdr, rules = next(iter(item.items()))
                    hdr_l = str(hdr).strip().lower()

                    # Always emit two flags in this order: [no <hdr>, bad <hdr>]
                    no_flag, bad_flag = "", ""

                    # HTTPS gating for https_headers
                    if category == "https_headers" and not is_https:
                        flags.extend([no_flag, bad_flag])
                        continue

                    # Presence (+ CSP enforce handling)
                    present = hdr_l in header_names
                    if not present:
                        # For CSP, allow Report-Only to satisfy presence only when
                        # enforce is False/absent
                        if hdr_l == "content-security-policy" and not rules.get(
                            "enforce"
                        ):
                            present = (
                                "content-security-policy-report-only" in header_names
                            )

                    if not present:
                        no_flag = "X"
                        flags.extend([no_flag, bad_flag])
                        continue

                    # Present -> evaluate rules
                    raw_val = headers_kv.get(hdr_l, "")

                    # Simple value rules (equals / one_of)
                    if "value" in rules and not _eval_value_rules(
                        rules["value"], raw_val
                    ):
                        bad_flag = "X"

                    # Params (e.g., HSTS)
                    if bad_flag == "" and "params" in rules:
                        params = _parse_semicolon_params(raw_val)
                        if not _eval_params_rules(rules["params"], params):
                            bad_flag = "X"

                    # CSP directives
                    if (
                        bad_flag == ""
                        and hdr_l == "content-security-policy"
                        and "directives" in rules
                    ):
                        csp = _parse_csp(raw_val)
                        if not _eval_csp_rules(rules["directives"], csp):
                            bad_flag = "X"

                    flags.extend([no_flag, bad_flag])
                    continue

                # Unknown pattern type -> ignore
                flags.append("")
            continue

        if category == "missing_pqc_kex":
            kex_raw = (extracted_by_category.get("kex_algorithms") or "").lower()
            kex_parts = [c.strip() for c in kex_raw.split(",") if c.strip()]
            if isinstance(patterns, dict):
                pat_iter = patterns.keys()
            else:
                pat_iter = patterns
            present = False
            for pat in pat_iter:
                p = str(pat).lower()
                if p in kex_parts or p in kex_raw:
                    present = True
                    break

            flags.append("X" if not present else "")
            continue
        if category == "max_validity":
            try:
                limit_days = int(str(patterns))
            except Exception:
                limit_days = None
            val_s = extracted_by_category.get("validity_days", "")
            try:
                validity_days = int(val_s) if val_s else None
            except ValueError:
                validity_days = None
            flags.append(
                "X"
                if (
                    limit_days is not None
                    and validity_days is not None
                    and validity_days > limit_days
                )
                else ""
            )
            continue
        if category == "weak_dh":
            try:
                threshold = int(str(patterns))
            except Exception:
                threshold = None
            bits_str = extracted_by_category.get("kex_dh_bits_min", "")
            try:
                bits = int(bits_str) if bits_str else None
            except ValueError:
                bits = None
            flags.append("X" if threshold and bits and bits < threshold else "")
            continue
        if category == "weak_curves":
            # YAML gives a list of curve names; we normalize by removing '-' and '_'
            curves_csv = extracted_by_category.get("kex_curves", "").lower()
            seen = {
                re.sub(r"[-_]", "", c.strip())
                for c in curves_csv.split(",")
                if c.strip()
            }
            pat_iter = patterns.keys() if isinstance(patterns, dict) else patterns
            weak = False
            for p in pat_iter:
                q = re.sub(r"[-_]", "", str(p).lower())
                if q in seen:
                    weak = True
                    break
            flags.append("X" if weak else "")
            continue
        if category == "hash_algorithms":
            cipher_src = extracted_by_category.get("cipher_features") or raw_content
            cipher_parts = [
                c.strip().lower() for c in cipher_src.split(",") if c.strip()
            ]
            cipher_hashes = _cipher_hashes_from(cipher_parts)
            for pat in patterns.keys() if isinstance(patterns, dict) else patterns:
                pat_l = str(pat).lower()
                cipher_match = pat_l in cipher_hashes
                sign_src = (extracted_by_category.get("sign_algo") or "").lower()
                sign_match = pat_l in sign_src
                flags.extend(["X" if cipher_match else "", "X" if sign_match else ""])
            continue
        if category == "kex_algorithms":
            for pat in patterns.keys() if isinstance(patterns, dict) else patterns:
                pat_l = str(pat).lower()
                if pat_l == "dh":
                    match = any("_dh_" in c for c in content_parts)
                elif pat_l == "ecdh":
                    match = any(
                        re.search(r"(^|[^a-z0-9])ecdh($|[^a-z0-9])", c.lower())
                        is not None
                        for c in content_parts
                    )
                else:
                    match = pat_l in raw_content
                flags.append("X" if match else "")
            continue
        if category == "weak_keys":
            if not isinstance(patterns, dict):
                flags.append("")  # defensive
                continue
            for pat in patterns.keys():
                threshold = patterns.get(pat)
                key_algo = extracted_by_category.get("key_algo", "")
                key_bits_str = extracted_by_category.get("key_size", "")
                try:
                    key_bits = int(key_bits_str) if key_bits_str else None
                except ValueError:
                    key_bits = None
                match = (
                    threshold is not None
                    and key_bits is not None
                    and _key_type_matches(pat, key_algo)
                    and key_bits < int(threshold)
                )
                flags.append("X" if match else "")
            continue

        # Generic fallback
        if isinstance(patterns, dict):
            pat_iter = patterns.keys()
        elif isinstance(patterns, (list, tuple, set)):
            pat_iter = patterns
        else:
            continue
        for pattern in pat_iter:
            pat_l = str(pattern).lower()
            match = pat_l in raw_content
            flags.append("X" if match else "")
    return flags


def extract_algorithms_generic(host, addr, script_id, yaml_cfg, out_rows):
    """Generic algorithm extractor for SSH, RDP and HTTP."""
    for p in _iter_ports(host):
        if p.get("protocol") != "tcp":
            continue
        script = p.find(f"script[@id='{script_id}']")
        if script is None:
            continue

        portid = p.get("portid")
        ip_port = f"{addr}:{portid}"

        meta_cols = []

        if script_id == "ssh2-enum-algos":
            extracted = {}
            for table in script.findall("table"):
                key = table.get("key")
                values = [_safe_text(e) for e in table.findall("elem")]
                extracted[key] = ", ".join([v for v in values if v])

            svc = p.find("service")
            product = svc.get("product", "") if svc is not None else ""
            version = svc.get("version", "") if svc is not None else ""
            ssh_version = " ".join(x for x in (product, version) if x).strip()
            meta_cols = [ssh_version]
        elif script_id == "rdp-enum-encryption":
            raw_output = script.get("output") or ""
            lower_output = raw_output.lower()
            extracted = {k: lower_output for k in yaml_cfg.keys()}
            m = re.search(
                r"(?im)^\s*rdp\s+protocol\s+version\s*:\s*(.*?)\s*(?:server)?\s*$",
                raw_output,
            )
            rdp_version = m.group(1).strip() if m else "Unknown"
            rdp_version = re.sub(r"\\s*server\\s*$", "", rdp_version, flags=re.I)
            meta_cols = [rdp_version]
        elif script_id == "http-headers":
            raw = script.get("output") or ""
            headers = {}
            for line in raw.splitlines():
                line = line.strip()
                if not line or ":" not in line:
                    continue
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()

            svc = p.find("service")
            name = (svc.get("name", "") if svc is not None else "").lower()
            tunnel = (svc.get("tunnel", "") if svc is not None else "").lower()
            is_https = (tunnel == "ssl") or (name == "https")
            header_csv = ", ".join(sorted(headers.keys()))
            extracted = {
                "http_headers": header_csv,
                "https_headers": header_csv,
                "is_https": "1" if is_https else "",
                "headers_dict": headers,
            }
        else:
            continue

        flags = _match_flags(extracted, yaml_cfg)
        out_rows.append([ip_port] + meta_cols + flags)


def extract_ssl_combined(host, addr, yaml_cfg, out_rows):
    """Merge ssl-enum-ciphers and ssl-cert info into a single row per TCP port."""
    for p in _iter_ports(host):
        if p.get("protocol") != "tcp":
            continue

        portid = p.get("portid")
        ip_port = f"{addr}:{portid}"

        s_enum = p.find("script[@id='ssl-enum-ciphers']")
        s_cert = p.find("script[@id='ssl-cert']")
        s_poodle = p.find("script[@id='ssl-poodle']")

        if s_enum is None and s_cert is None and s_poodle is None:
            continue

        # Canonical categories expected to match YAML keys directly
        extracted = {
            "cipher_features": "",
            "hash_algorithms": "",
            "kex_algorithms": "",
            "protocols": "",
            "status": "",
            "vulns": "",
        }

        # --- ssl-enum-ciphers
        if s_enum is not None:
            tls_versions = []
            cipher_texts = []
            dh_bits_seen = []
            curves_seen = set()

            for tls_table in s_enum.findall("table"):
                tls_key = (
                    tls_table.get("key") or ""
                ).lower()  # e.g., "tlsv1.2", "tlsv1.3"
                if tls_key.startswith(("ssl", "tls")):
                    tls_versions.append(tls_key)
                for c_parent in tls_table.findall("table[@key='ciphers']"):
                    for c_entry in c_parent.findall("table"):
                        name_elem = c_entry.find("elem[@key='name']")
                        if name_elem is not None and name_elem.text:
                            cipher_texts.append(name_elem.text.lower())

                        # Read kex_info to capture DH size and EC curve ---
                        kex_elem = c_entry.find("elem[@key='kex_info']")
                        kex_val = _safe_text(kex_elem).lower()
                        if kex_val:
                            # Nmap sometimes prefixes curves with "ecdh_"
                            if kex_val.startswith("ecdh_"):
                                kex_val = kex_val[5:]

                            # (1) Finite-field DH size: "dh 1024", "dh 2048"
                            m_dh = re.match(r"^dh\s*(\d+)$", kex_val)
                            if m_dh:
                                try:
                                    dh_bits_seen.append(int(m_dh.group(1)))
                                except ValueError:
                                    pass
                                continue

                            # (2) RFC 7919 named groups, e.g. "ffdhe2048" -> never weak
                            if re.match(r"^ffdhe\s*\d+$", kex_val):
                                # explicitly skip counting FFDHE groups as 'weak'
                                continue

                            # (3) Otherwise treat as EC curve and normalize formatting
                            curve_norm = re.sub(r"[-_]", "", kex_val).strip()
                            if curve_norm:
                                curves_seen.add(curve_norm)

            protocols_present = sorted(set(tls_versions))
            extracted["protocols"] = ", ".join(protocols_present)
            extracted["cipher_features"] = ", ".join(cipher_texts)
            # Preserve original behavior: reuse cipher list for hash/kex matching
            extracted["hash_algorithms"] = ", ".join(cipher_texts)
            extracted["kex_algorithms"] = ", ".join(cipher_texts)

            # Set missing protocols columns
            expected = [v.lower() for v in yaml_cfg.get("protocols_missing", [])]
            present = set(protocols_present)
            missing = [f"no {v}" for v in expected if v not in present]
            extracted["protocols_missing"] = ", ".join(missing)

            if dh_bits_seen:
                extracted["kex_dh_bits_min"] = str(min(dh_bits_seen))
            if curves_seen:
                extracted["kex_curves"] = ", ".join(sorted(curves_seen))

        # --- ssl-cert
        cert_cn = issuer = thumb = ""
        not_before = None
        not_after = None
        key_algo = key_bits = rsa_exp = sig_algo = ""

        if s_cert is not None:
            pem_elem = s_cert.find("elem[@key='pem']")
            cert_pem = _safe_text(pem_elem)
            meta = parse_ssl_cert_metadata(cert_pem)

            cert_cn = meta.subject_cn
            issuer = meta.issuer_cn
            thumb = meta.thumbprint
            not_before = meta.not_before
            not_after = meta.not_after
            key_algo = meta.key_algo
            key_bits = str(meta.key_size) if meta.key_size is not None else ""
            rsa_exp = str(meta.rsa_exponent) if meta.rsa_exponent is not None else ""
            sig_algo = meta.signature_algo
            extracted["sign_algo"] = sig_algo
            validity_days = None
            if not_before and not_after:
                try:
                    validity_days = (not_after - not_before).days
                except Exception:
                    validity_days = None
            if validity_days is not None:
                extracted["validity_days"] = str(validity_days)

            # When YAML contains hash names, also check signature algorithm string
            if "hash_algorithms" in yaml_cfg and meta.signature_algo:
                for hash_name in yaml_cfg["hash_algorithms"]:
                    if hash_name.lower() in meta.signature_algo.lower():
                        existing = extracted.get("hash_algorithms", "")
                        if hash_name.lower() not in existing:
                            extracted["hash_algorithms"] = (
                                f"{existing}, {hash_name}".strip(", ").strip()
                            )

            status_list = list(meta.status)
            if meta.revoked and "revoked" not in status_list:
                status_list.append("revoked")
            extracted["status"] = ", ".join(sorted(set(status_list)))
            extracted["key_algo"] = (key_algo or "").lower()
            extracted["key_size"] = key_bits

        if s_poodle is not None:
            poodle_vuln = False
            for t in s_poodle.findall("table"):
                st = t.find("elem[@key='state']")
                if (_safe_text(st) or "").strip().upper() == "VULNERABLE":
                    poodle_vuln = True
                    break
            if poodle_vuln:
                extracted["vulns"] = "poodle"

        # Build flags
        flags = _match_flags(extracted, yaml_cfg)

        # Meta columns (prefix)
        meta_cols = [
            cert_cn,
            issuer,
            thumb,
            not_before,
            not_after,
            key_algo,
            key_bits,
            rsa_exp,
            sig_algo,
        ]
        out_rows.append([ip_port] + meta_cols + flags)


def _build_algo_table(algo_rows, yaml_cfg, prefix_header=None):
    """
    Generic table builder for algorithm flags with optional meta prefix columns.

    - Always includes 'ip address' + prefix_header columns.
    - Includes only those flag columns that have at least one "X" across rows.
    """
    prefix_header = prefix_header or []
    prefix_count = len(prefix_header)

    base_header = ["ip address"] + prefix_header
    flag_columns = []
    for category, patterns in yaml_cfg.items():
        if category == "weak_keys" and isinstance(patterns, dict):
            for alg in patterns.keys():
                flag_columns.append("weak key size")
            continue
        if category == "weak_dh":
            flag_columns.append("weak dh")
            continue
        if category == "weak_curves":
            flag_columns.append("weak curve")
            continue
        if category == "max_validity":
            flag_columns.append("valid too long")
            continue
        if category == "missing_pqc_kex":
            flag_columns.append("no pqc kex")
            continue
        if category in ("headers", "http_headers", "https_headers"):
            pats = patterns
            if isinstance(pats, dict):
                pats_iter = [{k: v} for k, v in pats.items()]
            else:
                pats_iter = list(pats or [])

            for item in pats_iter:
                if isinstance(item, str):
                    p = item.strip().lower()
                    if p == "https_redir":
                        flag_columns.append("no https redir")
                    elif p == "hsts":
                        flag_columns.append("no hsts")
                    else:
                        flag_columns.append(f"no {p}")
                elif isinstance(item, dict) and item:
                    hdr = list(item.keys())[0].strip().lower()
                    flag_columns.append(f"no {hdr}")  # missing
                    flag_columns.append(f"bad {hdr}")  # present but fails rules
                else:
                    pass
            continue

        for pattern in patterns.keys() if isinstance(patterns, dict) else patterns:
            if "_missing" in category:
                col = f"no {pattern.lower()}"
                flag_columns.append(col)
            elif category == "hash_algorithms":
                flag_columns.append(f"cipher {pattern.lower()}")
                flag_columns.append(f"sign {pattern.lower()}")
            elif "kex" in category:
                col = f"kex {pattern.lower()}"
                flag_columns.append(col)
            else:
                col = pattern.lower()
                flag_columns.append(col)

    full_header = base_header + flag_columns

    # Determine which flag columns are used
    used_flag_indices = set()
    for row in algo_rows:
        for idx, val in enumerate(row[1 + prefix_count :], start=1 + prefix_count):
            if val == "X":
                used_flag_indices.add(idx)

    keep_indices = [0] + list(range(1, 1 + prefix_count)) + sorted(used_flag_indices)

    max_index = len(full_header) - 1
    keep_indices = [i for i in keep_indices if i <= max_index]
    filtered_header = [full_header[i] for i in keep_indices]

    table = PrettyTable()
    table.field_names = filtered_header
    table.align = "l"

    csv_out = []
    for row in algo_rows:
        filtered_row = [row[i] for i in keep_indices]
        table.add_row(filtered_row)
        csv_out.append(filtered_row)

    return table, csv_out, filtered_header


def _build_protocol_table(data, ports):
    """Build PrettyTable and CSV array for TCP/UDP open ports per host."""
    header = ["ip address"] + list(ports)
    table = PrettyTable()
    table.field_names = header
    table.align["ip address"] = "l"

    csv_out = []
    for ip_addr, open_ports in data:
        row = [ip_addr] + [("X" if str(p) in open_ports else "") for p in ports]
        table.add_row(row)
        csv_out.append(row)
    return table, csv_out, header


def _build_services_table(rows):
    header = ["ip address", "port", "proto", "service", "state"]
    table = PrettyTable()
    table.field_names = header
    table.align = "l"

    csv_out = []
    for r in rows:
        table.add_row(r)
        csv_out.append(list(r))
    return table, csv_out, header


def nmap_parser(args, root, workbook):
    """Main Nmap parser function."""
    data_nmap_tcp = []
    data_nmap_udp = []
    services_rows = []

    # Load YAML configurations
    data_package = "sr2t.data"

    ssh_algo_rows = []
    ssh_column_names = {
        "kex": "kex_algorithms",
        "missing_pqc_kex": "missing_pqc_kex",
        "cipher": "encryption_algorithms",
        "mac": "mac_algorithms",
        "compression": "compression_algorithms",
    }
    ssh_yaml = load_and_prepare_yaml(data_package, "nmap_ssh.yaml", ssh_column_names)

    rdp_algo_rows = []
    rdp_column_names = {
        "sec": "rdp_security_layer",
        "enc": "rdp_encryption_level",
        "proto": "rdp_protocol_version",
    }
    rdp_yaml = load_and_prepare_yaml(data_package, "nmap_rdp.yaml", rdp_column_names)

    ssl_algo_rows = []
    ssl_column_names = {
        "cipher": "cipher_features",
        "hash": "hash_algorithms",
        "kex": "kex_algorithms",
        "weak_dh": "weak_dh",
        "weak_curves": "weak_curves",
        "weak_keys": "weak_keys",
        "protocols": "protocols",
        "protocols_missing": "protocols_missing",
        "vulns": "vulns",
        "max_validity": "max_validity",
        "status": "status",
    }
    ssl_yaml = load_and_prepare_yaml(data_package, "nmap_ssl.yaml", ssl_column_names)

    http_algo_rows = []
    http_column_names = {
        "http_headers": "http_headers",
        "https_headers": "https_headers",
    }
    http_yaml = load_and_prepare_yaml(data_package, "nmap_http.yaml", http_column_names)

    # Parse hosts
    for element in root:
        for host in element.findall("host"):
            host_data = extract_host_data(host, args)
            addr = host_data.addr
            if not addr:
                continue

            # SSH, RDP, SSL extraction
            extract_algorithms_generic(
                host, addr, "ssh2-enum-algos", ssh_yaml, ssh_algo_rows
            )
            extract_algorithms_generic(
                host, addr, "rdp-enum-encryption", rdp_yaml, rdp_algo_rows
            )
            extract_algorithms_generic(
                host, addr, "http-headers", http_yaml, http_algo_rows
            )
            extract_ssl_combined(host, addr, ssl_yaml, ssl_algo_rows)

            # Services
            extract_services(host, args, addr, services_rows)

            if host_data.open_tcp_ports:
                data_nmap_tcp.append([addr, host_data.open_tcp_ports])
            if host_data.open_udp_ports:
                data_nmap_udp.append([addr, host_data.open_udp_ports])

    # Build sorted port lists
    tcp_ports = (
        sorted({int(p) for _, ports in data_nmap_tcp for p in ports})
        if data_nmap_tcp
        else []
    )
    udp_ports = (
        sorted({int(p) for _, ports in data_nmap_udp for p in ports})
        if data_nmap_udp
        else []
    )

    # Build tables
    nmap_tcp_table, csv_tcp, header_tcp = _build_protocol_table(
        data_nmap_tcp, tcp_ports
    )
    nmap_udp_table, csv_udp, header_udp = _build_protocol_table(
        data_nmap_udp, udp_ports
    )
    nmap_services_table, csv_services, header_services = _build_services_table(
        services_rows
    )

    ssh_prefix_header = ["ssh version"]
    ssh_table, csv_ssh, header_ssh = _build_algo_table(
        ssh_algo_rows, ssh_yaml, prefix_header=ssh_prefix_header
    )
    rdp_prefix_header = ["rdp version"]
    rdp_table, csv_rdp, header_rdp = _build_algo_table(
        rdp_algo_rows, rdp_yaml, prefix_header=rdp_prefix_header
    )
    http_table, csv_http, header_http = _build_algo_table(
        http_algo_rows, http_yaml, prefix_header=[]
    )
    ssl_prefix_header = [
        "cn / san",
        "issuer",
        "thumbprint",
        "not before",
        "not after",
        "key algo",
        "key size",
        "rsa exponent",
        "sign algo",
    ]
    ssl_table, csv_ssl, header_ssl = _build_algo_table(
        ssl_algo_rows,
        ssl_yaml,
        prefix_header=ssl_prefix_header,
    )

    # Host lists
    host_list_tcp = (
        [ip for ip, _ in data_nmap_tcp] if getattr(args, "nmap_host_list", 0) else []
    )
    host_list_udp = (
        [ip for ip, _ in data_nmap_udp] if getattr(args, "nmap_host_list", 0) else []
    )

    # Export (keeps current behavior & sheet names)
    exportables = [
        ("Nmap TCP", csv_tcp, header_tcp),
        ("Nmap UDP", csv_udp, header_udp),
        (
            ("Nmap Services", csv_services, header_services)
            if getattr(args, "nmap_services", 0) == 1
            else None
        ),
        ("ssh", csv_ssh, header_ssh),
        ("rdp", csv_rdp, header_rdp),
        ("ssl", csv_ssl, header_ssl),
        ("http", csv_http, header_http),
    ]
    export_all(args, workbook, [e for e in exportables if e])

    return (
        nmap_tcp_table if csv_tcp else [],
        nmap_udp_table if csv_udp else [],
        nmap_services_table if csv_services else [],
        host_list_tcp,
        host_list_udp,
        ssh_table if csv_ssh else [],
        rdp_table if csv_rdp else [],
        ssl_table if csv_ssl else [],
        http_table if csv_http else [],
        workbook,
    )
