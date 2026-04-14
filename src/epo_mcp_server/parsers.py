import logging
import re
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("epo_mcp_server.parsers")

def get_text(node: Any) -> str:
    """Helper to extract text from an OPS node, which can be a string or a {'$': 'value'} dict."""
    if isinstance(node, dict):
        return str(node.get("$", ""))
    return str(node) if node is not None else ""

def get_ns_key(data: Dict, key: str) -> Any:
    """Attempts to get a key from a dict, trying both the raw key and common prefixes."""
    if not isinstance(data, dict):
        return None
    if key in data:
        return data[key]
    
    # Try common prefixes
    for prefix in ["ops", "ftxt", "cpc", "ccd", "vrt", "reg"]:
        ns_key = f"{prefix}:{key}"
        if ns_key in data:
            return data[ns_key]
            
    # Also try without the prefix if the key provided was prefixed
    if ":" in key:
        return data.get(key.split(":")[-1])
    return None

def get_safe(data: Dict, path: List[Any], default: Any = None) -> Any:
    """Safely traverses a nested dictionary or list with namespace awareness."""
    current = data
    for key in path:
        if isinstance(current, dict):
            val = get_ns_key(current, str(key))
            current = val
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current if current is not None else default

def flatten_search_results(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    """Flattens a complex search result into a cleaner list of patents."""
    try:
        w_p_data = get_ns_key(raw_json, "world-patent-data") or {}
        bib_search = get_ns_key(w_p_data, "biblio-search") or {}
        search_res = get_ns_key(bib_search, "search-result") or {}
        
        # In search/biblio mode, we get a list of search-result objects
        results = search_res if isinstance(search_res, list) else [search_res]
        if not results or (len(results) == 1 and not results[0]):
             return {"total_results": 0, "patents": []}

        flattened_list = []
        for res in results:
            # The biblio data is nested inside exchange-documents for search/biblio
            ex_docs = get_ns_key(res, "exchange-documents") or []
            if isinstance(ex_docs, dict): ex_docs = [ex_docs]
            
            for ex_doc_wrapper in ex_docs:
                ex_doc = get_ns_key(ex_doc_wrapper, "exchange-document") or {}
                biblio = get_ns_key(ex_doc, "bibliographic-data") or {}
                
                # Get Document ID (EPODOC format preferred for MCP)
                p_num = ex_doc.get("@doc-number", "")
                p_country = ex_doc.get("@country", "")
                p_kind = ex_doc.get("@kind", "")
                
                pub_ref = get_ns_key(biblio, "publication-reference") or {}
                doc_ids = get_ns_key(pub_ref, "document-id") or []
                if isinstance(doc_ids, dict): doc_ids = [doc_ids]
                
                epodoc_id = ""
                for d in doc_ids:
                    if d.get("@document-id-type") == "epodoc":
                        epodoc_id = get_text(get_ns_key(d, "doc-number"))
                        break
                
                # Get Title
                titles = get_ns_key(biblio, "invention-title") or []
                if isinstance(titles, dict): titles = [titles]
                
                title_text = ""
                for t in titles:
                    if t.get("@lang") == "en" or not title_text:
                        title_text = get_text(t)
                
                flattened_list.append({
                    "id": epodoc_id or f"{p_country}{p_num}{p_kind}",
                    "title": title_text or "No Title Available",
                    "country": p_country,
                    "doc_number": p_num,
                    "kind": p_kind
                })
            
        return {
            "total_results": int(bib_search.get("@total-result-count", 0)),
            "patents": flattened_list
        }
    except Exception as e:
        logger.error(f"Error parsing search results: {e}")
        return {"error": "Parsing failed", "details": str(e)}

def clean_biblio(raw_json: Dict[str, Any]) -> Dict[str, Any]:
    """Cleans bibliographic data by extracting key fields and removing noise."""
    try:
        w_p_data = get_ns_key(raw_json, "world-patent-data") or {}
        exchange_docs = get_ns_key(w_p_data, "exchange-documents") or {}
        exchange = get_ns_key(exchange_docs, "exchange-document") or {}
        if isinstance(exchange, list):
            exchange = exchange[0]
            
        biblio = get_ns_key(exchange, "bibliographic-data") or {}
        
        # Titles
        titles = get_ns_key(biblio, "invention-title") or []
        if isinstance(titles, dict):
            titles = [titles]
        title_en = next((get_text(t) for t in titles if t.get("@lang") == "en"), get_text(titles[0]) if titles else "No Title")
        
        # Abstract
        abstract_node = get_ns_key(exchange, "abstract") or []
        if isinstance(abstract_node, dict):
            abstract_node = [abstract_node]
            
        abstract_en = ""
        for a in abstract_node:
            p_node = a.get("p", {})
            if isinstance(p_node, list):
                text = " ".join([get_text(p) for p in p_node])
            else:
                text = get_text(p_node)
            
            if a.get("@lang") == "en" or not abstract_en:
                abstract_en = text
                if a.get("@lang") == "en": break

        # Dates
        pub_ref = get_ns_key(biblio, "publication-reference") or {}
        # Try finding date in any available document-id
        doc_ids = get_ns_key(pub_ref, "document-id") or []
        if isinstance(doc_ids, dict): doc_ids = [doc_ids]
        pub_date = next((get_text(d.get("date")) for d in doc_ids if d.get("date")), "")

        # Parties (Applicants/Inventors)
        parties = get_ns_key(biblio, "parties") or {}
        
        # Applicants
        apps_node = get_ns_key(get_ns_key(parties, "applicants") or {}, "applicant") or []
        if isinstance(apps_node, dict): apps_node = [apps_node]
        applicants = []
        for a in apps_node:
            name_node = get_ns_key(get_ns_key(a, "applicant-name") or {}, "name")
            name_text = get_text(name_node)
            if name_text and name_text not in applicants:
                applicants.append(name_text)

        # Inventors
        invs_node = get_ns_key(get_ns_key(parties, "inventors") or {}, "inventor") or []
        if isinstance(invs_node, dict): invs_node = [invs_node]
        inventors = []
        for i in invs_node:
            name_node = get_ns_key(get_ns_key(i, "inventor-name") or {}, "name")
            name_text = get_text(name_node)
            if name_text and name_text not in inventors:
                inventors.append(name_text)

        return {
            "title": title_en,
            "abstract": truncate_text(abstract_en, 2000),
            "publication_date": pub_date,
            "applicants": applicants,
            "inventors": inventors,
            "doc_id": exchange.get("@doc-id", "Unknown")
        }
    except Exception as e:
         logger.error(f"Error parsing biblio: {e}")
         return {"error": "Parsing failed", "details": str(e)}

def parse_image_links(raw_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parses the EPO OPS images constituent to find direct scan links."""
    try:
        w_p_data = get_ns_key(raw_json, "world-patent-data") or {}
        images = get_ns_key(w_p_data, "document-instance") or []
        
        if not images:
            # Fallback for search nested images
            images = get_safe(w_p_data, ["biblio-search", "search-result", "document-instance"], [])
        
        if isinstance(images, dict):
            images = [images]
            
        links = []
        for img in images:
            links.append({
                "type": img.get("@desc", "Unknown"),
                "format": img.get("@format", "Unknown"),
                "pages": img.get("@number-of-pages", "1"),
                "link": img.get("@link", "")
            })
        return links
    except Exception as e:
        logger.error(f"Error parsing image links: {e}")
        return []

def parse_citations(raw_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parses citation information (patcit and nplcit) from biblio data."""
    try:
        w_p_data = get_ns_key(raw_json, "world-patent-data") or {}
        exchange_docs = get_ns_key(w_p_data, "exchange-documents") or {}
        exchange = get_ns_key(exchange_docs, "exchange-document") or {}
        if isinstance(exchange, list):
            exchange = exchange[0]
            
        biblio = get_ns_key(exchange, "bibliographic-data") or {}
        refs_cited = get_ns_key(biblio, "references-cited") or {}
        citations = get_ns_key(refs_cited, "citation") or []
        
        return parse_citations_list(citations)
    except Exception as e:
        logger.error(f"Error parsing citations: {e}")
        return []

def parse_fulltext(raw_json: Dict[str, Any], component: str, limit: bool = True) -> Union[List[str], str]:
    """Parses full-text (claims or description) into a clean list of strings or a single string."""
    try:
        w_p_data = get_ns_key(raw_json, "world-patent-data") or {}
        ft_docs = get_ns_key(w_p_data, "fulltext-documents") or {}
        ft_doc = get_ns_key(ft_docs, "fulltext-document") or {}
        if isinstance(ft_doc, list): ft_doc = ft_doc[0]
        
        content_node = get_ns_key(ft_doc, component) or {}
        
        if component == "claims":
            claims_list = get_ns_key(content_node, "claim") or []
            if isinstance(claims_list, dict): claims_list = [claims_list]
            
            parsed_claims = []
            for c in claims_list:
                texts = get_ns_key(c, "claim-text") or []
                if isinstance(texts, dict): texts = [texts]
                elif isinstance(texts, str): texts = [{"$": texts}]
                
                # If we have multiple claim-text items, they might be individual claims or lines
                # Let's collect them all first
                all_text = "\n".join([get_text(t) for t in texts])
                
                # Try to split by claim numbers (e.g., "2. ", "15. ") if it looks like they are bundled
                # but only if we don't already have a clean list from multiple <claim> tags
                if len(claims_list) == 1:
                    # Split by "Number. " pattern at start of lines
                    parts = re.split(r'\n(?=\d+\.)|(?<=^)(?=\d+\.)', all_text)
                    for p in parts:
                        p = p.strip()
                        if p: parsed_claims.append(p)
                else:
                    parsed_claims.append(all_text.strip())
            
            if limit:
                return [c for c in parsed_claims if c][:50]
            return [c for c in parsed_claims if c]
            
        elif component == "description":
            p_nodes = get_ns_key(content_node, "p") or []
            if isinstance(p_nodes, dict): p_nodes = [p_nodes]
            
            full_description = "\n\n".join([get_text(p) for p in p_nodes])
            if limit:
                return truncate_text(full_description, 8000)
            return full_description
            
        return ""
    except Exception as e:
        logger.error(f"Error parsing fulltext ({component}): {e}")
        return [] if component == "claims" else ""

def parse_ccd(raw_json: Dict[str, Any], limit: bool = True) -> List[Dict[str, Any]]:
    """Parses Common Citation Document (CCD) data into a consolidated list unique of citations."""
    try:
        w_p_data = get_ns_key(raw_json, "world-patent-data") or {}
        ccd_node = get_ns_key(w_p_data, "ccd") or {}
        members = get_ns_key(ccd_node, "family-member") or []
        if isinstance(members, dict): members = [members]
        
        consolidated_citations = []
        seen_ids = set() # To avoid duplicate citations across family members
        
        for member in members:
            pub_ref = get_ns_key(member, "publication-reference")
            member_id = "unknown"
            if pub_ref:
                doc_ids = get_ns_key(pub_ref, "document-id") or []
                if isinstance(doc_ids, dict): doc_ids = [doc_ids]
                for doc in doc_ids:
                    if doc.get("@document-id-type") == "epodoc":
                        member_id = get_text(get_ns_key(doc, "doc-number"))
                        break
            
            refs_cited = get_ns_key(member, "references-cited") or {}
            citations = get_ns_key(refs_cited, "citation") or []
            if citations:
                parsed_list = parse_citations_list(citations)
                for c in parsed_list:
                    # Key for uniqueness: type + doc_id/text
                    cit_key = f"{c['type']}_{c.get('doc_id') or c.get('text')}"
                    if cit_key not in seen_ids:
                        c["found_in_member"] = member_id
                        consolidated_citations.append(c)
                        seen_ids.add(cit_key)
                        
                    # Token efficiency: stop if we have a lot of citations
                    if limit and len(consolidated_citations) >= 40: break
            if limit and len(consolidated_citations) >= 40: break
                    
        return consolidated_citations
    except Exception as e:
        logger.error(f"Error parsing CCD: {e}")
        return []

def parse_citations_list(citations: Union[List[Dict[str, Any]], Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Helper to parse a list of citation nodes into a clean list of dicts."""
    if not isinstance(citations, list):
        if isinstance(citations, dict): citations = [citations]
        else: return []
        
    parsed = []
    for cit in citations:
        cited_by = cit.get("@cited-by", "unknown")
        cited_phase = cit.get("@cited-phase", "unknown")
        
        # Patent Citations
        patcit = get_ns_key(cit, "patcit")
        if patcit:
            doc_ids = get_ns_key(patcit, "document-id") or []
            if isinstance(doc_ids, dict): doc_ids = [doc_ids]
            
            doc_num = ""
            for doc in doc_ids:
                if doc.get("@document-id-type") == "epodoc":
                    doc_num = get_text(get_ns_key(doc, "doc-number"))
                    break
            if not doc_num and doc_ids:
                doc_num = get_text(get_ns_key(doc_ids[0], "doc-number"))
            
            category = get_text(get_ns_key(cit, "category"))
            
            parsed.append({
                "type": "patent",
                "cited_by": cited_by,
                "cited_phase": cited_phase,
                "doc_id": doc_num,
                "category": category,
                "num": patcit.get("@num")
            })
            
        # Non-Patent Citations
        nplcit = get_ns_key(cit, "nplcit")
        if nplcit:
            text = get_text(get_ns_key(nplcit, "text"))
            parsed.append({
                "type": "npl",
                "cited_by": cited_by,
                "cited_phase": cited_phase,
                "text": text,
                "num": nplcit.get("@num")
            })
    return parsed

def parse_register(raw_json: Dict[str, Any], limit: bool = True) -> Dict[str, Any]:
    """Parses European Patent Register data into a summary of status and proceedings."""
    try:
        w_p_data = get_ns_key(raw_json, "world-patent-data") or {}
        reg_search = get_ns_key(w_p_data, "register-search") or {}
        reg_docs = get_ns_key(reg_search, "register-documents") or {}
        reg_doc = get_ns_key(reg_docs, "register-document") or {}
        if isinstance(reg_doc, list): reg_doc = reg_doc[0]
        
        status = reg_doc.get("@status", "Unknown")
        statuses = get_ns_key(reg_doc, "ep-patent-statuses") or {}
        status_list = get_ns_key(statuses, "ep-patent-status") or []
        if isinstance(status_list, dict): status_list = [status_list]
        
        proceedings = []
        proc_data = get_ns_key(reg_doc, "procedural-data") or []
        if isinstance(proc_data, dict): proc_data = [proc_data]
        for proc in proc_data:
            steps = get_ns_key(proc, "procedural-step") or []
            if isinstance(steps, dict): steps = [steps]
            for step in steps:
                date = get_ns_key(step, "date")
                code = step.get("@procedural-step-code")
                desc_node = get_ns_key(step, "step-description")
                proceedings.append({
                    "date": get_text(date), 
                    "description": get_text(desc_node)
                })
                
        events = []
        events_data = get_ns_key(reg_doc, "events-data") or []
        if isinstance(events_data, dict): events_data = [events_data]
        for event_grp in events_data:
             evt_list = get_ns_key(event_grp, "event") or []
             if isinstance(evt_list, dict): evt_list = [evt_list]
             for evt in evt_list:
                 date = get_ns_key(evt, "date")
                 desc_node = get_ns_key(evt, "event-description")
                 events.append({
                     "date": get_text(date), 
                     "description": get_text(desc_node)
                 })

        if limit:
            return {
                "current_status": status,
                "status_history": [{"date": s.get("@change-date"), "text": get_text(s)} for s in status_list][-5:],
                "recent_proceedings": proceedings[-10:] if proceedings else [], 
                "recent_events": events[-10:] if events else []
            }
        
        return {
            "current_status": status,
            "status_history": [{"date": s.get("@change-date"), "text": get_text(s)} for s in status_list],
            "all_proceedings": proceedings, 
            "all_events": events
        }
    except Exception as e:
        logger.error(f"Error parsing register: {e}")
        return {"error": str(e)}

def parse_claim_dependencies(claims: List[str]) -> List[Dict[str, Any]]:
    """Analyzes a list of claims and identifies dependencies between them via basic text analysis.
    
    Returns:
        A list of dicts with claim number, text sample, and identified parent claim numbers.
    """
    if not claims:
        return []
        
    structured_claims = []
    # Pattern to find numbers in phrases like "claim 1", "claims 1 and 2", etc.
    dep_pattern = re.compile(r"claim[s]?\s*(\d+(?:\s*(?:,|and|or|to)\s*\d+)*)", re.IGNORECASE)
    
    for i, claim_text in enumerate(claims):
        claim_num = i + 1
        matches = dep_pattern.findall(claim_text)
        
        dependencies = []
        for match in matches:
            # Extract all numbers from the match string
            nums = re.findall(r"\d+", match)
            for n in nums:
                n_int = int(n)
                # A claim usually only depends on a LOWER numbered claim
                if n_int < claim_num and n_int not in dependencies:
                    dependencies.append(n_int)
        
        structured_claims.append({
            "claim_num": claim_num,
            "dependencies": sorted(dependencies),
            "text": claim_text[:300] + "..." if len(claim_text) > 300 else claim_text
        })
        
    return structured_claims

def truncate_text(text: str, max_chars: int = 5000) -> str:
    """Truncates text and adds a note if it was shortened."""
    if not text:
        return ""
    if len(text) > max_chars:
        return text[:max_chars] + f"\n\n[... TEXT TRUNCATED. Use a more specific query for sections ...]"
    return text
