import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

class RAGLaptopRecommender:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df.columns = self.df.columns.str.strip()
        self.df.fillna("", inplace=True)

        self.df["price"] = (
            self.df["price"].astype(str)
            .str.replace(",", "", regex=False)
            .str.extract(r"(\d+)")
            .fillna(0)
            .astype(int)
        )

        self.df["rating"] = (
            self.df["rating"]
            .astype(str)
            .str.extract(r"(\d+\.?\d*)")
            .fillna(0)
            .astype(float)
        )

        self.df["text"] = self.df.apply(
            lambda row: (
                f"{row['name']} with {row['Processor']} Gen {row['Processor_Gen']} processor, "
                f"{row['RAM']} {row['RAM_Type']} RAM, {row['SSD']} SSD, {row['Display_Size']} display, "
                f"{row['Operating_System']}, {row['Graphics']} graphics, ₹{row['price']} price, "
                f"{row['rating']} rating. {row['Other_Specs']} {row['Description']}"
            ), axis=1
        )

        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = self.model.encode(self.df["text"].tolist(), show_progress_bar=True)

        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def recommend(self, query, top_k=5):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, top_k * 10)
        retrieved = self.df.iloc[indices[0]]
        retrieved = retrieved.drop_duplicates(subset="name")
        return retrieved.head(top_k).to_dict(orient="records")

    def get_laptop_summary(self, top_k=10):
        """Return a text summary of top_k laptops"""
        summary = ""
        for i, row in self.df.head(top_k).iterrows():
            summary += (
                f"{i+1}. {row['name']}, {row['Processor']} Gen {row['Processor_Gen']}, "
                f"{row['RAM']} {row['RAM_Type']} RAM, {row['SSD']} SSD, "
                f"{row['Graphics']} graphics, ₹{row['price']}, {row['rating']}⭐\n"
            )
        return summary
