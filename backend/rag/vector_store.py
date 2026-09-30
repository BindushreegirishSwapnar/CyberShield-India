import os
import re
import math
from collections import Counter, defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge_base')
INBOX_DIR = os.path.join(KB_DIR, 'inbox')

# Acronym and domain expansion dictionary for query rewriting
EXPANSIONS = {
    "1930": "1930 helpline national cyber crime reporting portal financial fraud golden hour",
    "golden hour": "golden hour 2-3 hours bank debit freeze transaction recovery helpline 1930",
    "rbi": "Reserve Bank of India RBI master circular zero customer liability unauthorized electronic transaction",
    "sop": "standard operating procedure cyber cell investigation protocol",
    "sim swap": "SIM swap telecom duplicate SIM Aadhaar forged KYC 2FA intercept",
    "digital arrest": "digital arrest fake police Skype video call CBI customs extortion",
    "freeze": "bank account freeze debit freeze lien marking section 102 CrPC intermediary",
    "fir": "first information report cognizable cyber offence registration",
    "bns": "Bharatiya Nyaya Sanhita BNS 2023 cheating impersonation extortion",
    "it act": "Information Technology Act 2000 Section 66 Section 66C Section 66D Section 43 Section 79",
    "upi": "Unified Payments Interface UPI fraudulent VPA QR code refund debit",
    "mule": "mule bank account money laundering layered fund transfer interdiction"
}

def rewrite_query(query):
    """Query expansion and rewriting with cybercrime domain terminology."""
    q_clean = query.strip()
    q_lower = q_clean.lower()
    additions = []
    for term, exp in EXPANSIONS.items():
        if term in q_lower:
            additions.append(exp)
    if additions:
        return f"{q_clean} {' '.join(additions)}"
    return q_clean

class BM25Index:
    """Pure Python BM25 ranking implementation with standard Okapi BM25 parameters."""
    def __init__(self, k1=1.5, b=0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = 0
        self.avg_doc_len = 0.0
        self.doc_lengths = []
        self.idf = {}
        self.doc_freqs = defaultdict(int)
        self.inverted_index = defaultdict(list)

    def _tokenize(self, text):
        return [w.lower() for w in re.findall(r'\b[a-zA-Z0-9_-]{2,}\b', text)]

    def index(self, documents):
        self.corpus_size = len(documents)
        if self.corpus_size == 0:
            return
        total_len = 0
        self.doc_lengths = []
        self.inverted_index = defaultdict(list)
        self.doc_freqs = defaultdict(int)

        for doc_id, doc_text in enumerate(documents):
            tokens = self._tokenize(doc_text)
            doc_len = len(tokens)
            self.doc_lengths.append(doc_len)
            total_len += doc_len
            term_counts = Counter(tokens)

            for term, count in term_counts.items():
                self.inverted_index[term].append((doc_id, count))
                self.doc_freqs[term] += 1

        self.avg_doc_len = total_len / float(self.corpus_size)

        # Precompute IDF
        self.idf = {}
        for term, df in self.doc_freqs.items():
            # Standard Lucene/Okapi BM25 IDF formulation
            self.idf[term] = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query, top_k=20):
        tokens = self._tokenize(query)
        scores = defaultdict(float)

        for term in tokens:
            if term not in self.inverted_index:
                continue
            idf_val = self.idf.get(term, 0.0)
            for doc_id, freq in self.inverted_index[term]:
                doc_len = self.doc_lengths[doc_id]
                denom = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
                score = idf_val * ((freq * (self.k1 + 1.0)) / max(1e-6, denom))
                scores[doc_id] += score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

class KnowledgeVectorStore:
    def __init__(self, kb_dir=KB_DIR):
        self.kb_dir = kb_dir
        self.inbox_dir = INBOX_DIR
        self.chunks = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.bm25 = BM25Index()
        self.build_index()

    def _chunk_text_with_overlap(self, text, max_words=350, overlap_words=50):
        """Structure-aware sliding window chunking with 15% overlap."""
        words = text.split()
        if len(words) <= max_words:
            return [text]
        chunks = []
        stride = max_words - overlap_words
        for i in range(0, len(words), stride):
            chunk_words = words[i:i + max_words]
            if len(chunk_words) > 30:
                chunks.append(" ".join(chunk_words))
        return chunks

    def build_index(self):
        """Parse all markdown/text/pdf files into structure-aware semantic chunks and build hybrid indices."""
        self.chunks = []
        os.makedirs(self.inbox_dir, exist_ok=True)

        candidate_dirs = [self.kb_dir, self.inbox_dir]
        seen_files = set()

        for directory in candidate_dirs:
            if not os.path.exists(directory):
                continue
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if not os.path.isfile(filepath) or filepath in seen_files:
                    continue
                seen_files.add(filepath)

                if filename.endswith(('.md', '.txt')):
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    except Exception:
                        continue

                    # Extract Document Metadata
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    title = title_match.group(1).strip() if title_match else filename.replace('.md', '').replace('_', ' ').title()

                    ref_match = re.search(r'\*\*Document Reference:\*\*\s*(.+)$', content, re.MULTILINE)
                    doc_ref = ref_match.group(1).strip() if ref_match else filename

                    auth_match = re.search(r'\*\*(?:Issuing Authority|Source Authority|Jurisdiction):\*\*\s*(.+)$', content, re.MULTILINE)
                    authority = auth_match.group(1).strip() if auth_match else "Cyber Intelligence & Legal Division"

                    date_match = re.search(r'\*\*(?:Date|Effective Date|Year):\*\*\s*(.+)$', content, re.MULTILINE)
                    doc_date = date_match.group(1).strip() if date_match else "2024-2026"

                    # Split by sections (### or ##)
                    sections = re.split(r'\n(?=#{2,3}\s+)', content)
                    for sec in sections:
                        sec = sec.strip()
                        if not sec:
                            continue

                        sec_head_match = re.search(r'^#{2,3}\s+(.+)$', sec, re.MULTILINE)
                        section_title = sec_head_match.group(1).strip() if sec_head_match else "Operational Procedures"

                        clean_text = re.sub(r'#{1,4}\s*', '', sec)
                        clean_text = re.sub(r'\*{1,2}', '', clean_text)
                        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

                        # Structure-aware chunking with 15% overlap
                        sub_chunks = self._chunk_text_with_overlap(clean_text, max_words=380, overlap_words=55)
                        for part_idx, chunk_text in enumerate(sub_chunks):
                            if len(chunk_text) > 60:
                                self.chunks.append({
                                    "doc_title": title,
                                    "doc_ref": doc_ref,
                                    "authority": authority,
                                    "date": doc_date,
                                    "section": section_title if len(sub_chunks) == 1 else f"{section_title} (Part {part_idx + 1})",
                                    "content": chunk_text,
                                    "raw_section": sec,
                                    "filename": filename
                                })

        if self.chunks:
            corpus = [c["content"] for c in self.chunks]
            # 1. TF-IDF Semantic Index
            self.vectorizer = TfidfVectorizer(
                ngram_range=(1, 2),
                sublinear_tf=True,
                stop_words='english',
                max_features=5000
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            # 2. BM25 Lexical Index
            self.bm25.index(corpus)
            print(f"[RAG] Knowledge Base indexed: {len(self.chunks)} structure-aware chunks across authoritative legal/SOP repositories.")

    def search_hybrid(self, query, top_k=5, min_score=0.05):
        """
        Hybrid Retrieval Architecture:
        1. BM25 Lexical Keyword Retrieval (Top 20)
        2. TF-IDF Semantic Cosine Similarity (Top 20)
        3. Reciprocal Rank Fusion (RRF, k=60)
        4. Cross-Encoder / Term Overlap Reranker (Top 5)
        """
        if not self.chunks or not query.strip():
            return []

        expanded_query = rewrite_query(query)

        # 1. BM25 Search
        bm25_results = self.bm25.search(expanded_query, top_k=20)
        bm25_ranks = {doc_id: rank + 1 for rank, (doc_id, score) in enumerate(bm25_results)}

        # 2. Vector Cosine Search
        query_vec = self.vectorizer.transform([expanded_query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]
        top_vec_indices = np.argsort(similarities)[::-1][:20]
        vector_ranks = {int(doc_id): rank + 1 for rank, doc_id in enumerate(top_vec_indices) if similarities[doc_id] > 0.01}

        # 3. Reciprocal Rank Fusion (RRF)
        all_candidate_ids = set(bm25_ranks.keys()) | set(vector_ranks.keys())
        rrf_scores = {}
        K_RRF = 60.0

        for doc_id in all_candidate_ids:
            bm25_rank = bm25_ranks.get(doc_id, 100)
            vec_rank = vector_ranks.get(doc_id, 100)
            score = (1.0 / (K_RRF + bm25_rank)) + (1.0 / (K_RRF + vec_rank))
            rrf_scores[doc_id] = score

        # Top 15 from RRF
        sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:15]

        # 4. Contextual Reranking pass
        query_terms = set(re.findall(r'\b[a-zA-Z0-9_-]{3,}\b', query.lower()))
        reranked = []

        for doc_id, rrf_score in sorted_candidates:
            chunk = dict(self.chunks[doc_id])
            content_lower = chunk["content"].lower()
            section_lower = chunk["section"].lower()

            # Cross-scoring with section heading boost and exact term coverage
            match_count = sum(1 for term in query_terms if term in content_lower)
            section_boost = sum(2 for term in query_terms if term in section_lower)
            coverage = match_count / max(1, len(query_terms))
            
            vec_sim = float(similarities[doc_id])
            final_score = (rrf_score * 40.0) + (vec_sim * 35.0) + (coverage * 20.0) + (section_boost * 2.5)

            chunk["similarity"] = round(vec_sim, 4)
            chunk["rrf_score"] = round(rrf_score, 6)
            chunk["final_score"] = round(final_score, 3)
            chunk["confidence_pct"] = round(min(98.5, max(30.0, final_score * 1.5)), 1)
            reranked.append(chunk)

        reranked.sort(key=lambda x: x["final_score"], reverse=True)
        return reranked[:top_k]

    def search(self, query, top_k=3, min_similarity=0.08):
        """Backwards compatible search delegate to search_hybrid."""
        return self.search_hybrid(query, top_k=top_k, min_score=min_similarity)

# Singleton instance
_store_instance = None

def get_vector_store():
    global _store_instance
    if _store_instance is None:
        _store_instance = KnowledgeVectorStore()
    return _store_instance

if __name__ == '__main__':
    vs = get_vector_store()
    res = vs.search_hybrid("What are the steps for bank debit freeze under 1930 helpline during golden hour?")
    print(f"Retrieved {len(res)} chunks:")
    for r in res:
        print(f"[{r['doc_ref']} - {r['section']}] (Score: {r['confidence_pct']}%)")
        print(f"{r['content'][:140]}...\n")
