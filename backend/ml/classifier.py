import re
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import numpy as np
import joblib
import os

class TransactionClassifier:
    """ML-based transaction category classifier for FinSight"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
        # Training data - hardcoded seed dataset for Indian spending patterns
        self.training_data = [
            # Food & Dining
            ("ordered biryani from zomato", "Food"),
            ("swiggy delivery charge", "Food"),
            ("domino's pizza order", "Food"),
            ("restaurant bill at mainland china", "Food"),
            ("mcdonald's meal", "Food"),
            ("tea at tapri", "Food"),
            ("coffee at starbucks", "Food"),
            ("grocery shopping at big bazaar", "Food"),
            ("vegetables from sabzi mandi", "Food"),
            ("milk and bread from dairy", "Food"),
            
            # Transportation
            ("ola cab ride to airport", "Transport"),
            ("uber auto to office", "Transport"),
            ("metro card recharge", "Transport"),
            ("petrol pump payment", "Transport"),
            ("auto rickshaw fare", "Transport"),
            ("train ticket irctc", "Transport"),
            ("ola bike rental", "Transport"),
            ("rapido bike ride", "Transport"),
            ("bus pass monthly", "Transport"),
            ("parking fee", "Transport"),
            
            # Shopping
            ("amazon order", "Shopping"),
            ("flipkart purchase", "Shopping"),
            ("myntra clothes shopping", "Shopping"),
            ("ajio online shopping", "Shopping"),
            ("tata cliq purchase", "Shopping"),
            ("meesho order", "Shopping"),
            ("nykaa cosmetics", "Shopping"),
            ("reliance digital voucher", "Shopping"),
            ("croma electronics", "Shopping"),
            
            # Entertainment
            ("netflix subscription", "Entertainment"),
            ("amazon prime video", "Entertainment"),
            ("hotstar subscription", "Entertainment"),
            ("spotify premium", "Entertainment"),
            ("youtube premium", "Entertainment"),
            ("movie tickets pvr", "Entertainment"),
            ("concert ticket bookmyshow", "Entertainment"),
            ("game purchase steam", "Entertainment"),
            
            # Bills & Utilities
            ("electricity bill bescom", "Utilities"),
            ("water bill delhi jal", "Utilities"),
            ("gas cylinder bharat gas", "Utilities"),
            ("internet connection airtel", "Utilities"),
            ("mobile recharge jio", "Utilities"),
            ("dth subscription tata play", "Utilities"),
            ("society maintenance", "Utilities"),
            ("municipal tax", "Utilities"),
            
            # Healthcare
            ("apollo pharmacy medicine", "Healthcare"),
            ("doctor consultation fee", "Healthcare"),
            ("hospital bill max healthcare", "Healthcare"),
            ("diagnostic test dr lal path", "Healthcare"),
            ("health insurance premium", "Healthcare"),
            ("medicine purchase netmeds", "Healthcare"),
            ("dental clinic visit", "Healthcare"),
            
            # Education
            ("coursera subscription", "Education"),
            ("udemy course purchase", "Education"),
            ("byju's premium", "Education"),
            ("unacademy plus", "Education"),
            ("school fees", "Education"),
            ("textbook purchase", "Education"),
            ("online course payment", "Education"),
            ("exam fee", "Education"),
            
            # Investment & Income
            ("sip investment zerodha", "Investment"),
            ("mutual fund sip", "Investment"),
            ("stock purchase groww", "Investment"),
            ("fixed deposit interest", "Investment"),
            ("ppf contribution", "Investment"),
            ("epf deduction", "Investment"),
            ("dividend received", "Income"),
            ("salary credit", "Income"),
            ("freelance payment", "Income"),
            ("rental income", "Income"),
            ("bonus amount", "Income"),
            ("interest income", "Income"),
            
            # Other
            ("atm withdrawal", "Other"),
            ("bank charges", "Other"),
            ("cash withdrawal", "Other"),
            ("gift expense", "Other"),
            ("donation payment", "Other"),
            ("miscellaneous expense", "Other"),
        ]
        
        # Categories: model can predict
        self.categories = [
            "Food", "Transport", "Shopping", "Entertainment", 
            "Utilities", "Healthcare", "Education", 
            "Investment", "Income", "Other"
        ]
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess transaction description"""
        # Convert to lowercase and remove special characters
        text = text.lower().strip()
        
        # Remove common transaction patterns that don't help classification
        patterns_to_remove = [
            r'\b\d{2,4}-\d{2,4}-\d{4}\b',  # dates
            r'\b\d+\.\d+\b',  # amounts
            r'\b(inr|rs|₹)\b',  # currency symbols
            r'\b(txn|transaction|payment)\b',  # generic terms
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def train(self):
        """Train the classifier with hardcoded data"""
        try:
            # Prepare training data
            descriptions = [self._preprocess_text(desc) for desc, _ in self.training_data]
            categories = [cat for _, cat in self.training_data]
            
            # Encode labels
            self.label_encoder.fit(categories)
            encoded_labels = self.label_encoder.transform(categories)
            
            # Create and train pipeline
            self.model = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    lowercase=True
                )),
                ('classifier', LogisticRegression(
                    random_state=42,
                    max_iter=1000
                ))
            ])
            
            self.model.fit(descriptions, encoded_labels)
            self.is_trained = True
            
            # Save the model
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            joblib.dump({
                'model': self.model,
                'label_encoder': self.label_encoder,
                'categories': self.categories
            }, os.path.join(model_dir, 'transaction_classifier.pkl'))
            
            return True
            
        except Exception as e:
            print(f"Error training model: {e}")
            return False
    
    def load_model(self):
        """Load pre-trained model"""
        try:
            model_dir = os.path.join(os.path.dirname(__file__), 'models')
            model_path = os.path.join(model_dir, 'transaction_classifier.pkl')
            
            if os.path.exists(model_path):
                data = joblib.load(model_path)
                self.model = data['model']
                self.label_encoder = data['label_encoder']
                self.categories = data['categories']
                self.is_trained = True
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict_category(self, description: str) -> Tuple[str, float]:
        """Predict category for transaction description"""
        try:
            if not self.is_trained:
                # Try to load model if not already loaded
                if not self.load_model():
                    return "Other", 0.0
            
            # Preprocess input
            processed_text = self._preprocess_text(description)
            
            # Make prediction
            prediction = self.model.predict([processed_text])
            probabilities = self.model.predict_proba([processed_text])
            
            # Decode prediction
            predicted_category = self.label_encoder.inverse_transform(prediction)[0]
            confidence = float(np.max(probabilities[0]))
            
            return predicted_category, confidence
            
        except Exception as e:
            print(f"Error predicting category: {e}")
            return "Other", 0.0
    
    def get_training_data(self) -> List[Dict]:
        """Return training data for API endpoint"""
        return [
            {"description": desc, "category": cat} for desc, cat in self.training_data
        ]
    
    def get_categories(self) -> List[str]:
        """Return all available categories"""
        return self.categories

# Global classifier instance
classifier = TransactionClassifier()

# Initialize model on startup
if not classifier.is_trained:
    classifier.train()
