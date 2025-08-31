from __future__ import annotations
from ..imports import *
from .path_utils import *

# Return:
# {
#   'entries': [ { 'path', 'line', 'col', 'severity', 'code', 'message' }, ... ],
#   'errors':  [...subset...],
#   'warnings':[...subset...],
# }
ERROR_PHRASES   = ['does not','cannot','has no','must be']
WARNING_PHRASES = ['is declared']

DEMOTE_CODES = {'TS6133'}  # treat these as warnings
def _compile_phrase_rx(phrases):
    phrases = [p.strip() for p in phrases or [] if p.strip()]
    if not phrases:
        return None
    # case-insensitive, word-ish boundaries; escape phrases safely
    pat = r'(?i)(?<!\w)(?:' + '|'.join(re.escape(p) for p in phrases) + r')(?!\w)'
    return re.compile(pat)

_ERR_RX = _compile_phrase_rx(ERROR_PHRASES)
_WRN_RX = _compile_phrase_rx(WARNING_PHRASES)
def get_tripple_string(string):
    nustring = ''
    for i in range(3):
        nustring +=string
    return nustring
def get_within_quotes(text,quotes=None):
    quotes_strings = quotes or ["'",'"']
    in_quotes = []
    for quotes_string in quotes_strings:
        if not isinstance(quotes_string,list):
            tripple= get_tripple_string(quotes_string)
            texts = [text]
            if tripple in text:
                texts= text.split(tripple)
            for text_part in texts:
                quote_count = len(text_part) - len(text_part.replace(quotes_string,''))
                quote_spl = text_part.split(quotes_string)
                in_quotes+=[quote_spl[i] for i in range(quote_count) if ((i == 1 or i%2 != float(0)) and len(quote_spl) > i)]
        else:
            texts= text.split(quotes_string[0])
            for text in texts:
                in_quotes.append(text.split(quotes_string[1])[0])
    return in_quotes

def _phrase_hit(msg, rx):
    return bool(rx.search(msg)) if (rx and msg) else False
def parse_tsc_output(
    text: str,
    *,
    error_phrases: list[str] = None,
    warning_phrases: list[str] = None,
    require_phrase_match: bool = False,
    escalate_warning_on_error_phrase: bool = True,
    demote_error_on_warning_phrase: bool = True,      # NEW
    demote_codes: set[str] = DEMOTE_CODES,            # NEW
) -> Dict[str, Any]:
    if not text:
        return {'entries': [], 'errors': [], 'warnings': []}

    # (allow caller to override)
    err_rx = _compile_phrase_rx(error_phrases) if error_phrases is not None else _ERR_RX
    wrn_rx = _compile_phrase_rx(warning_phrases) if warning_phrases is not None else _WRN_RX

    pat1 = re.compile(r"""^(?P<path>.+?)\((?P<line>\d+),(?P<col>\d+)\):\s+
                          (?P<severity>error|warning)\s+
                          (?P<code>TS\d+)\s*:\s*(?P<msg>.+)$""",
                      re.IGNORECASE | re.VERBOSE)
    pat2 = re.compile(r"""^(?P<path>.+?):(?P<line>\d+):(?P<col>\d+)\s*-\s*
                          (?P<severity>error|warning)\s+
                          (?P<code>TS\d+)\s*:\s*(?P<msg>.+)$""",
                      re.IGNORECASE | re.VERBOSE)
    pat3_head = re.compile(r"^(?P<severity>error|warning)\s*:\s*(?P<msg>.+)$", re.IGNORECASE)
    pat3_loc  = re.compile(r"^\s*at\s+(?P<path>.+?):(?P<line>\d+):(?P<col>\d+)\s*:?\s*$", re.IGNORECASE)

    entries = []
    pending = None
    for line in text.splitlines():
        m = pat1.match(line) or pat2.match(line)
        if m:
            d = m.groupdict()
            msg = d['msg']
            sev = d['severity'].lower()
            code = d['code']  # like 'TS6133'
            
            hit_err = _phrase_hit(msg, err_rx)
            hit_wrn = _phrase_hit(msg, wrn_rx)

            # demote certain "errors" to warnings
            if demote_error_on_warning_phrase and sev == 'error':
                if hit_wrn or (code and code in (demote_codes or set())):
                    sev = 'warning'

            # optional escalation (warnings that look like real errors)
            if escalate_warning_on_error_phrase and sev == 'warning' and hit_err:
                sev = 'error'

            # optional filter: require a phrase hit in the corresponding list
            if require_phrase_match:
                ok = (sev == 'error'   and (hit_err or not err_rx)) or \
                     (sev == 'warning' and (hit_wrn or not wrn_rx))
                if not ok:
                    continue

            entries.append({
                'path': d['path'],
                'line': int(d['line']),
                'col':  int(d['col']),
                'severity': sev,
                'code': code,
                'msg': msg,
                'vars': get_within_quotes(line),
                'hit_error_phrase': hit_err,
                'hit_warning_phrase': hit_wrn,
            })
            pending = None
            continue

        # Vite/esbuild two-line format
        m = pat3_head.match(line)
        if m:
            pending = {'severity': m.group('severity').lower(), 'msg': m.group('msg')}
            continue
        if pending:
            m = pat3_loc.match(line)
            if m:
                msg = pending['msg']
                sev = pending['severity']
                hit_err = _phrase_hit(msg, err_rx)
                hit_wrn = _phrase_hit(msg, wrn_rx)
                # no code in this format; phrase only
                if demote_error_on_warning_phrase and sev == 'error' and hit_wrn:
                    sev = 'warning'
                if escalate_warning_on_error_phrase and sev == 'warning' and hit_err:
                    sev = 'error'
                if require_phrase_match:
                    ok = (sev == 'error'   and (hit_err or not err_rx)) or \
                         (sev == 'warning' and (hit_wrn or not wrn_rx))
                    if not ok:
                        pending = None
                        continue

                entries.append({
                    'path': m.group('path'),
                    'line': int(m.group('line')),
                    'col':  int(m.group('col')),
                    'severity': sev,
                    'code': None,
                    'msg': msg,
                    'vars': get_within_quotes(line),
                    'hit_error_phrase': hit_err,
                    'hit_warning_phrase': hit_wrn,
                })
                pending = None

    errors   = [e for e in entries if e['severity'] == 'error']
    warnings = [e for e in entries if e['severity'] == 'warning']
    return {'entries': entries, 'errors': errors, 'warnings': warnings}

def get_error_type(e):
    is_error = False
    is_warning = False
    if e['severity'] == 'error':
        is_error = True
    elif e['severity'] == 'warning':
        is_warning = True
    return is_error,is_warning
def get_errors(e,
               only_errors=None,
               only_warnings=None,
               require_error_phrase=False,
               require_warning_phrase=False
               ):
    is_error,is_warning = get_error_type(e)
    if is_error == True:
        if require_error_phrase and not e['hit_error_phrase']:
            return 
        if only_errors == True or (only_errors == None and only_warnings == None):
            return e

    if is_warning == True:
        if require_warning_phrase and not e['hit_warning_phrase']:
            return 
        if only_warnings == True or (only_errors == None and only_warnings == None):
            return e
def filter_entries(entries,
                   *,
                   only_errors=None,     # True/False/None
                   only_warnings=None,     # True/False/None
                   require_error_phrase=False,
                   require_warning_phrase=False):
    out = []
    for e in entries:
        e = get_errors(e,
               only_errors=only_errors,
               only_warnings=only_warnings,
               require_error_phrase=require_error_phrase,
               require_warning_phrase=require_warning_phrase
              ) 
           
        if e:
            out.append(e)
    return out
def format_entry_for_log(e: dict) -> str:
    code = f" {e['code']}" if e.get('code') else ""
    # use 'msg' (that’s what you saved) not 'message'
    return f"{e['severity'].upper()}{code}: {e['path']}:{e['line']}:{e['col']} — {e.get('msg','')}"


def get_entry_output(last_output: str):
    last_output = last_output or ""
    # parse & split to errors/warnings for filtering and lists
    # parse & split to errors/warnings for filtering and lists
    res = parse_tsc_output(last_output)
    parsed_entries = res.get('entries')
    res["errors"] = filter_entries(parsed_entries, only_errors=True, require_error_phrase=False)
    res["warnings"] = filter_entries(parsed_entries, only_warnings=True, require_warning_phrase=False)
    res["all"] = res["errors"]+res["warnings"]

    res["errors_only"]   = "\n".join(format_entry_for_log(e) for e in res["errors"])
    res["warnings_only"] = "\n".join(format_entry_for_log(e) for e in res["warnings"])
    res["all_only"] = "\n".join(format_entry_for_log(e) for e in res["all"])
    # refresh visible lists
    res["error_entries"] = [(e.get('path',''), e.get('line',''), e.get('col',''), e.get('msg',''), e.get('code',''), e.get('vars','')) for e in res["errors"]]
    res["warning_entries"] = [(e.get('path',''), e.get('line',''), e.get('col',''), e.get('msg',''), e.get('code',''), e.get('vars','')) for e in res["warnings"]]
    res["all_entries"]= res["error_entries"]+res["warning_entries"]
    return res
