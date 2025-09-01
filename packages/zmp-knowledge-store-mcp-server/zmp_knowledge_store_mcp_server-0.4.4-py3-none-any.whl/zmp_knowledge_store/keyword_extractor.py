"""
Advanced keyword extraction for technical documentation

Supports multiple extraction methods with solution-specific optimization
"""

import re
from typing import List, Dict, Any
from collections import Counter
import logging

# Optional imports
try:
    from nltk.tokenize import word_tokenize
    from nltk.tag import pos_tag

    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from keybert import KeyBERT

    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Advanced keyword extraction for technical documentation"""

    def __init__(self, solution_type: str = None) -> None:
        self.solution_type = solution_type.lower() if solution_type else None
        self.setup_domain_vocabularies()

        # Initialize advanced models if available
        if KEYBERT_AVAILABLE:
            try:
                self.keybert_model = KeyBERT()
            except Exception as e:
                logger.warning(f"KeyBERT initialization failed: {e}")
                self.keybert_model = None
        else:
            self.keybert_model = None

        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                logger.warning("spaCy model not found")
                self.nlp = None
        else:
            self.nlp = None

    def setup_domain_vocabularies(self) -> None:
        """Setup solution-specific technical vocabularies"""

        self.technical_terms = {
            "infrastructure",
            "deployment",
            "configuration",
            "monitoring",
            "authentication",
            "authorization",
            "security",
            "scalability",
            "performance",
            "integration",
            "automation",
            "orchestration",
            "microservices",
            "containers",
            "kubernetes",
            "cloud",
            "devops",
        }

        self.solution_vocabularies = {
            "zcp": {
                "container",
                "kubernetes",
                "k8s",
                "cluster",
                "pod",
                "deployment",
                "service",
                "ingress",
                "namespace",
                "configmap",
                "secret",
                "helm",
                "kubectl",
                "docker",
                "registry",
                "orchestration",
                "cicd",
                "pipeline",
                "modernization",
                "cloud-native",
                "rbac",
            },
            "amdp": {
                "devops",
                "automation",
                "platform",
                "engineering",
                "development",
                "modernization",
                "application",
                "lifecycle",
                "workflow",
                "reusable",
                "components",
                "self-service",
                "portal",
                "toolchain",
                "infrastructure",
                "deployment",
                "continuous",
                "delivery",
            },
            "apim": {
                "api",
                "gateway",
                "management",
                "endpoint",
                "microservice",
                "rest",
                "soap",
                "graphql",
                "oauth",
                "jwt",
                "token",
                "throttling",
                "rate-limiting",
                "monitoring",
                "analytics",
                "documentation",
                "swagger",
                "openapi",
                "versioning",
                "cors",
            },
        }

        self.acronyms = {
            "api",
            "rest",
            "soap",
            "http",
            "https",
            "ssl",
            "tls",
            "jwt",
            "oauth",
            "saml",
            "ldap",
            "cicd",
            "devops",
            "msa",
            "soa",
            "k8s",
            "yaml",
            "json",
            "xml",
            "cpu",
            "ram",
            "rbac",
        }

    def get_optimal_keyword_count(self, content: str) -> int:
        """Determine optimal keyword count based only on content length."""
        word_count = len(content.split())
        if word_count < 200:
            return 5
        elif word_count < 600:
            return 8
        else:
            return 10

    def extract_keywords(self, content: str) -> List[str]:
        """Main keyword extraction method with adaptive count."""
        max_keywords = self.get_optimal_keyword_count(content)
        # Try advanced methods first, fallback to simple
        if self.keybert_model:
            try:
                return self.extract_keybert_keywords(content, max_keywords)
            except Exception:
                pass
        if self.nlp:
            try:
                return self.extract_spacy_keywords(content, max_keywords)
            except Exception:
                pass
        return self.extract_combined_keywords(content, max_keywords)

    def extract_combined_keywords(self, content: str, max_keywords: int) -> List[str]:
        """Combined extraction using multiple methods"""
        text = self.clean_text(content)
        words = text.split()

        filtered_words = [word.lower() for word in words if self.is_valid_keyword(word)]

        word_freq = Counter(filtered_words)
        boosted_keywords = self.boost_domain_terms(word_freq)

        # Add manual extraction
        manual_keywords = self.extract_manual_keywords(content)
        for keyword in manual_keywords:
            boosted_keywords[keyword] = boosted_keywords.get(keyword, 0) + 3

        return [word for word, _ in boosted_keywords.most_common(max_keywords)]

    def extract_keybert_keywords(self, content: str, max_keywords: int) -> List[str]:
        """KeyBERT-based extraction"""
        keywords = self.keybert_model.extract_keywords(
            content,
            keyphrase_ngram_range=(1, 2),
            stop_words="english",
            top_k=max_keywords * 2,
            use_mmr=True,
            diversity=0.5,
        )

        processed_keywords = []
        for keyword, score in keywords:
            keyword = keyword.lower()
            boost = self.calculate_domain_boost(keyword)
            processed_keywords.append((keyword, score * boost))

        processed_keywords.sort(key=lambda x: x[1], reverse=True)
        return [keyword for keyword, _ in processed_keywords[:max_keywords]]

    def extract_spacy_keywords(self, content: str, max_keywords: int) -> List[str]:
        """spaCy-based extraction with NER"""
        doc = self.nlp(content)
        keywords = set()

        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG", "PERSON", "GPE"]:
                if self.is_valid_keyword(ent.text):
                    keywords.add(ent.text.lower())

        # Extract important tokens
        for token in doc:
            if (
                token.pos_ in ["NOUN", "PROPN", "ADJ"]
                and not token.is_stop
                and self.is_valid_keyword(token.lemma_)
            ):
                keywords.add(token.lemma_.lower())

        keyword_scores = {kw: self.calculate_domain_boost(kw) for kw in keywords}

        sorted_keywords = sorted(
            keyword_scores.items(), key=lambda x: x[1], reverse=True
        )
        return [word for word, _ in sorted_keywords[:max_keywords]]

    def extract_nltk_keywords(self, content: str, max_keywords: int) -> List[str]:
        """NLTK-based extraction using POS tagging"""
        if not NLTK_AVAILABLE:
            return self.extract_combined_keywords(content, max_keywords)

        try:
            # Tokenize and POS tag
            tokens = word_tokenize(content.lower())
            pos_tags = pos_tag(tokens)

            # Extract nouns, adjectives, and technical terms
            keywords = []
            for word, pos in pos_tags:
                if pos in [
                    "NN",
                    "NNS",
                    "NNP",
                    "NNPS",
                    "JJ",
                    "JJR",
                    "JJS",
                ] and self.is_valid_keyword(word):
                    keywords.append(word)

            # Count and boost domain terms
            word_freq = Counter(keywords)
            boosted_keywords = self.boost_domain_terms(word_freq)

            return [word for word, _ in boosted_keywords.most_common(max_keywords)]

        except Exception as e:
            logger.warning(f"NLTK extraction failed: {e}")
            return self.extract_combined_keywords(content, max_keywords)

    def extract_manual_keywords(self, content: str) -> List[str]:
        """Manual extraction of domain-specific terms"""
        content_lower = content.lower()
        found_keywords = []

        # Solution-specific terms
        if self.solution_type:
            solution_terms = self.solution_vocabularies.get(self.solution_type, set())
            for term in solution_terms:
                if term in content_lower:
                    found_keywords.append(term)

        # Technical terms
        for term in self.technical_terms:
            if term in content_lower:
                found_keywords.append(term)

        # Acronyms
        for acronym in self.acronyms:
            if re.search(r"\b" + acronym.upper() + r"\b", content):
                found_keywords.append(acronym)

        return found_keywords

    def calculate_domain_boost(self, keyword: str) -> float:
        """Calculate domain-specific boost for keywords"""
        boost = 1.0

        if keyword in self.technical_terms:
            boost *= 1.5
        if keyword in self.acronyms:
            boost *= 1.3
        if self.solution_type and keyword in self.solution_vocabularies.get(
            self.solution_type, set()
        ):
            boost *= 2.0

        return boost

    def boost_domain_terms(self, word_freq: Counter) -> Counter:
        """Boost domain-specific terms in frequency counter"""
        boosted = Counter()
        for word, freq in word_freq.items():
            boost = self.calculate_domain_boost(word)
            boosted[word] = int(freq * boost)
        return boosted

    def clean_text(self, text: str) -> str:
        """Clean text for processing"""
        text = re.sub(r"http[s]?://\S+", " ", text)
        text = re.sub(r"\S+@\S+", " ", text)
        text = re.sub(r"[^\w\s-]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def is_valid_keyword(self, word: str) -> bool:
        """Check if word is valid for keyword extraction"""
        if not word or len(word) < 2:
            return False

        word_lower = word.lower()
        stopwords_set = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "this",
            "that",
            "these",
            "those",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "could",
            "can",
            "may",
        }

        return (
            word_lower not in stopwords_set
            and not word.isdigit()
            and word.replace("-", "").replace("_", "").isalnum()
        )

    def extract_tfidf_keywords(self, content: str, max_keywords: int) -> List[str]:
        """TF-IDF based keyword extraction"""
        words = self.clean_text(content).split()

        # Calculate term frequency
        word_count = len(words)
        tf_scores = {}
        for word in words:
            word = word.lower()
            if self.is_valid_keyword(word):
                tf_scores[word] = tf_scores.get(word, 0) + 1

        # Normalize TF scores
        for word in tf_scores:
            tf_scores[word] = tf_scores[word] / word_count

        # Simple IDF approximation (boost rare technical terms)
        idf_boost = {}
        for word in tf_scores:
            if word in self.technical_terms or word in self.acronyms:
                idf_boost[word] = 2.0
            elif self.solution_type and word in self.solution_vocabularies.get(
                self.solution_type, set()
            ):
                idf_boost[word] = 3.0
            else:
                idf_boost[word] = 1.0

        # Calculate final scores
        final_scores = {}
        for word in tf_scores:
            final_scores[word] = tf_scores[word] * idf_boost.get(word, 1.0)

        # Sort and return top keywords
        sorted_keywords = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_keywords[:max_keywords]]

    def analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content characteristics for keyword extraction optimization"""
        words = content.split()
        return {
            "word_count": len(words),
            "unique_words": len(set(word.lower() for word in words)),
            "technical_density": len(self.extract_manual_keywords(content)) / len(words)
            if words
            else 0,
            "avg_word_length": sum(len(word) for word in words) / len(words)
            if words
            else 0,
            "complexity_score": self.calculate_complexity_score(content),
        }

    def calculate_complexity_score(self, content: str) -> float:
        """Calculate content complexity score (0-1)"""
        words = content.split()
        if not words:
            return 0.0

        # Factors contributing to complexity
        avg_word_length = sum(len(word) for word in words) / len(words)
        long_sentences = len(
            [s for s in re.split(r"[.!?]+", content) if len(s.split()) > 20]
        )
        technical_density = len(self.extract_manual_keywords(content)) / len(words)
        unique_word_ratio = len(set(words)) / len(words)

        # Normalize and combine factors
        complexity = (
            min(avg_word_length / 10, 1.0) * 0.2
            + min(long_sentences / 10, 1.0) * 0.3
            + min(technical_density * 10, 1.0) * 0.3
            + unique_word_ratio * 0.2
        )

        return min(complexity, 1.0)
