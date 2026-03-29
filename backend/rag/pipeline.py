import os
import asyncio
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from app.database.database import get_db
from app.core.config import settings


# Finance Knowledge Base - hardcoded Q&A pairs
FINANCE_KNOWLEDGE_BASE = [
    {
        "question": "What is the 50/30/20 budgeting rule?",
        "answer": "The 50/30/20 rule is a budgeting framework where you allocate 50% of your after-tax income to needs (rent, utilities, groceries), 30% to wants (dining out, entertainment), and 20% to savings and debt repayment. This helps maintain financial balance while ensuring you're building wealth for the future."
    },
    {
        "question": "How much should I save for an emergency fund?",
        "answer": "You should save 3-6 months of essential living expenses in your emergency fund. This includes rent/mortgage, utilities, food, transportation, and minimum debt payments. Keep this money in a liquid, easily accessible account like a high-yield savings account, not invested in the stock market."
    },
    {
        "question": "What's the difference between SIP and lumpsum investment?",
        "answer": "SIP (Systematic Investment Plan) involves investing fixed amounts regularly (monthly), which averages out purchase cost through rupee cost averaging. Lumpsum means investing a large amount at once. SIPs are better for regular income earners and reduce timing risk, while lumpsum works well when you have a large corpus and markets are at low levels."
    },
    {
        "question": "Which is better: index funds or individual stocks?",
        "answer": "Index funds are generally better for most investors because they offer diversification, lower costs, and track market performance. Individual stocks require research, time, and carry higher concentration risk. Index funds are ideal for long-term wealth creation, while individual stocks might suit experienced investors with high risk tolerance."
    },
    {
        "question": "How can I save tax under Section 80C?",
        "answer": "Under Section 80C, you can claim deductions up to ₹1.5 lakh through ELSS mutual funds (₹1.5L), PPF (₹1.5L), EPF contributions, life insurance premiums, home loan principal repayment, and NSC. ELSS offers the best returns among these with a 3-year lock-in period and potential for 12-15% annual returns."
    },
    {
        "question": "What's the difference between NSE and BSE?",
        "answer": "NSE (National Stock Exchange) and BSE (Bombay Stock Exchange) are India's two main stock exchanges. NSE is larger by trading volume and introduced derivatives trading. BSE is Asia's oldest exchange (established 1875) and has more listed companies. Most stocks trade on both exchanges, but Nifty 50 (NSE) and Sensex (BSE) are their respective benchmark indices."
    },
    {
        "question": "How does compound interest work?",
        "answer": "Compound interest is interest earned on both your principal amount and accumulated interest. For example, ₹1 lakh at 10% annually becomes ₹1.10 lakh in year 1, then earns 10% on ₹1.10 lakh in year 2, not just the original ₹1 lakh. This creates exponential growth - the Rule of 72 says your money doubles in 72/interest_rate years."
    },
    {
        "question": "What's the best strategy to pay off debt?",
        "answer": "Two popular strategies: Avalanche method (pay highest interest debt first to save money) and Snowball method (pay smallest balances first for psychological wins). For most Indians, prioritize high-interest debt like credit cards (36-48%) and personal loans (12-20%) over home loans (8-10%) which offer tax benefits."
    },
    {
        "question": "How can I improve my credit score?",
        "answer": "Improve your credit score by: paying all bills on time (35% weight), keeping credit utilization below 30% (30% weight), maintaining old credit accounts (15% weight), having a mix of secured/unsecured loans (10%), and limiting new credit applications (10%). Check your CIBIL report quarterly and dispute any errors."
    },
    {
        "question": "What is asset allocation?",
        "answer": "Asset allocation is dividing your investment portfolio across different asset classes based on risk tolerance and goals. A common rule: 100 - your age = percentage in equities. At 30, invest 70% in equities, 30% in debt. Rebalance annually to maintain target allocation and manage risk."
    },
    {
        "question": "Should I rent or buy a house?",
        "answer": "Buy if you plan to stay 5+ years, have 20% down payment, and EMI is <30% of income. Rent if you need flexibility, have <20% down payment, or property prices are overvalued. Consider total cost: EMI + maintenance + property tax vs rent + investment of down payment difference."
    },
    {
        "question": "What are mutual funds and how do they work?",
        "answer": "Mutual funds pool money from many investors to invest in stocks, bonds, or other assets. They're managed by professionals who create a diversified portfolio. You buy units, NAV (Net Asset Value) is calculated daily. Types include equity (high risk/return), debt (moderate), and hybrid (balanced). They offer diversification even with small investments starting from ₹500."
    },
    {
        "question": "How much should I invest for retirement?",
        "answer": "Follow the 15% rule: invest 15% of your annual income for retirement. For early retirement at 45, increase to 25-30%. Assuming 12% returns, investing ₹15,000 monthly from age 25 can create ₹10+ crore by age 60. Start early - the power of compounding means starting at 25 vs 35 can result in 3x more wealth."
    },
    {
        "question": "What's the difference between saving and investing?",
        "answer": "Saving is putting money aside for short-term goals (1-3 years) in safe instruments like FDs, savings accounts. Investing is putting money to work for long-term growth (5+ years) through assets like stocks, mutual funds. Savings preserve capital with low returns (3-7%), investing grows capital with higher returns (10-15%+) but carries risk."
    },
    {
        "question": "How do I calculate my net worth?",
        "answer": "Net worth = Total Assets - Total Liabilities. Assets include cash, bank balance, investments (mutual funds, stocks), property value, gold. Liabilities include home loan, car loan, credit card dues, personal loans. Track quarterly - positive and growing net worth indicates financial health."
    },
    {
        "question": "What is inflation and how does it affect me?",
        "answer": "Inflation is the rate at which prices increase, reducing purchasing power. India's average inflation is 4-6%. If inflation is 6% and your FD gives 7%, real return is only 1%. To beat inflation, invest in equities (12-15% long-term returns) rather than keeping too much in cash or FDs."
    },
    {
        "question": "Should I prepay my home loan?",
        "answer": "Prepay if: home loan rate >8%, you have emergency fund, and no higher-interest debt. Don't prepay if: rate <7%, you get tax benefits on interest, or you can earn >12% elsewhere. Consider partial prepayment to reduce EMI rather than closing the loan completely."
    },
    {
        "question": "What are tax-saving investments for salaried employees?",
        "answer": "For salaried employees: Section 80C (₹1.5L) - ELSS, PPF, EPF; Section 80D (₹25K) - health insurance; Section 80E - education loan interest; HRA exemption for rent; LTA for travel. Standard deduction of ₹50K is automatic. Maximize 80C with ELSS for best returns + tax savings."
    },
    {
        "question": "How do I start investing with ₹5000 per month?",
        "answer": "Start with SIPs: ₹3000 in an index fund (Nifty 50), ₹1500 in ELSS for tax saving, ₹500 in a debt fund for stability. Use direct plans to save 1-1.5% commission. Increase amount by 10% annually. Focus on consistency over timing - even ₹5000/month for 25 years at 12% creates ₹1.3 crore."
    },
    {
        "question": "What is financial independence and how to achieve it?",
        "answer": "Financial independence means having enough investments to cover living expenses without working. Calculate your FIRE number: Annual expenses × 25. If expenses are ₹8L/year, you need ₹2 crore. Achieve by: saving 50%+ income, investing in equities, increasing income, and keeping expenses low. Start early - financial independence at 45 requires aggressive saving and investing."
    }
]


class RAGPipeline:
    def __init__(self):
        self.collection = None
        self.client = None
        self.genai_model = None
        self._initialize_chroma()
        self._initialize_gemini()
        
    def _initialize_chroma(self):
        """Initialize ChromaDB with finance knowledge base"""
        try:
            print("DEBUG: Initializing ChromaDB...")
            self.client = chromadb.Client(Settings(is_persistent=False))
            self.collection = self.client.create_collection(name="finsight_kb")
            
            # Prepare documents for embedding
            documents = []
            metadatas = []
            ids = []
            
            for i, qa in enumerate(FINANCE_KNOWLEDGE_BASE):
                doc_text = f"Q: {qa['question']}\nA: {qa['answer']}"
                documents.append(doc_text)
                metadatas.append({"question": qa["question"], "type": "qa_pair"})
                ids.append(f"qa_{i}")
            
            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"DEBUG: ChromaDB initialized with {len(documents)} documents")
            
        except Exception as e:
            print(f"Failed to initialize ChromaDB: {e}")
            self.collection = None
    
    def _initialize_gemini(self):
        """Initialize Gemini AI"""
        try:
            api_key = settings.gemini_api_key
            print(f"DEBUG: Gemini API key from settings: {api_key[:10]}..." if api_key else "DEBUG: No Gemini API key in settings")
            if api_key:
                genai.configure(api_key=api_key)
                self.genai_model = genai.GenerativeModel('gemini-2.5-flash')
                print("DEBUG: Gemini model initialized successfully")
            else:
                print("Gemini API key not found")
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")
            self.genai_model = None
    
    def get_user_context(self, user_id: int, db) -> str:
        """Generate user financial context summary"""
        try:
            # Get user's financial data
            # This would need to be implemented based on your actual database schema
            print(f"DEBUG: Getting context for user {user_id}")
            # For now, returning a placeholder
            context = "User financial context is being calculated..."
            print(f"DEBUG: Generated context: {context}")
            return context
        except Exception as e:
            print(f"Error getting user context: {e}")
            return "User financial context unavailable."
    
    def _is_finance_related(self, question: str) -> bool:
        """Check if question is finance-related"""
        finance_keywords = [
            'money', 'finance', 'investment', 'saving', 'budget', 'expense', 'income',
            'tax', 'loan', 'emi', 'credit', 'debit', 'bank', 'mutual fund', 'stock',
            'share', 'portfolio', 'wealth', 'retirement', 'insurance', 'gold', 'property',
            'inflation', 'interest', 'dividend', 'capital', 'asset', 'liability',
            'savings', 'expense', 'salary', 'business', 'profit', 'loss', 'rupee', '₹',
            'rs', 'amount', 'cost', 'price', 'fund', 'scheme', 'sip', 'lumpsum'
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in finance_keywords)
    
    async def answer_finance_question(self, question: str, user_context: str = "") -> Dict[str, any]:
        """Main RAG function to answer finance questions"""
        try:
            print(f"DEBUG: Received question: {question}")
            print(f"DEBUG: Gemini model available: {self.genai_model is not None}")
            print(f"DEBUG: ChromaDB available: {self.collection is not None}")
            
            # Check if question is finance-related
            if not self._is_finance_related(question):
                return {
                    "answer": "I can only help with personal finance questions.",
                    "sources_used": 0,
                    "fallback": False
                }
            
            # Check if Gemini is available
            if not self.genai_model:
                return {
                    "answer": "AI chat requires Gemini API key configuration.",
                    "sources_used": 0,
                    "fallback": False
                }
            
            retrieved_chunks = []
            sources_used = 0
            
            # Try to get relevant chunks from ChromaDB
            if self.collection:
                try:
                    results = self.collection.query(
                        query_texts=[question],
                        n_results=3
                    )
                    
                    if results['documents'] and results['documents'][0]:
                        retrieved_chunks = results['documents'][0]
                        sources_used = len(retrieved_chunks)
                except Exception as e:
                    print(f"ChromaDB query failed: {e}")
            
            # Build prompt
            system_prompt = """You are FinSight, an AI assistant specializing in personal finance for Indian users. 
            Provide accurate, practical, and clear financial advice. Be concise but thorough. 
            Focus on Indian context (tax rules, investment options, regulations). 
            Always mention risks where applicable. Never give guaranteed return promises."""
            
            context_text = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No specific knowledge base matches found."
            
            full_prompt = f"""{system_prompt}

User Context: {user_context}

Relevant Financial Information:
{context_text}

User Question: {question}

Please provide a helpful answer based on the information above and your general financial knowledge. Be specific to Indian context where relevant."""
            
            # Call Gemini with timeout
            try:
                print(f"DEBUG: Calling Gemini with prompt length: {len(full_prompt)}")
                response = await asyncio.wait_for(
                    asyncio.to_thread(self.genai_model.generate_content, full_prompt),
                    timeout=15.0
                )
                answer = response.text
                print(f"DEBUG: Gemini response received, length: {len(answer)}")
            except asyncio.TimeoutError:
                print("DEBUG: Gemini API timeout")
                answer = "I'm taking too long to respond. Please try a simpler question."
            except Exception as e:
                print(f"Gemini API error: {e}")
                print(f"DEBUG: Error type: {type(e).__name__}")
                answer = "I encountered an error while processing your question. Please try again."
            
            return {
                "answer": answer,
                "sources_used": sources_used,
                "fallback": not bool(retrieved_chunks)
            }
            
        except Exception as e:
            print(f"Error in answer_finance_question: {e}")
            return {
                "answer": "I encountered an unexpected error. Please try again later.",
                "sources_used": 0,
                "fallback": True
            }


# Global instance - initialize safely
rag_pipeline = None
try:
    print("🔄 Initializing RAG pipeline...")
    rag_pipeline = RAGPipeline()
    print("✅ RAG pipeline initialized successfully")
except Exception as e:
    print(f"❌ RAG pipeline initialization failed: {e}")
    print("⚠️ AI chat functionality will be disabled")
    rag_pipeline = None
