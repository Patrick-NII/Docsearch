from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

class TextSplitter:
    """Découpeur de texte intelligent"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialise le découpeur de texte
        
        Args:
            chunk_size: Taille maximale de chaque chunk
            chunk_overlap: Chevauchement entre les chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def split_documents(self, documents: list) -> list:
        """
        Découpe une liste de documents en chunks
        
        Args:
            documents: Liste des documents à découper
            
        Returns:
            Liste des chunks
        """
        all_chunks = []
        
        for document in documents:
            chunks = self.split_document(document)
            all_chunks.extend(chunks)
        
        logger.info(f"Total de {len(all_chunks)} chunks créés à partir de {len(documents)} documents")
        
        # Filtrer les chunks vides ou trop courts
        filtered_chunks = self.filter_chunks(all_chunks)
        logger.info(f"Filtrage: {len(all_chunks)} -> {len(filtered_chunks)} chunks")
        
        return filtered_chunks
    
    def split_document(self, document: dict) -> list:
        """
        Découpe un document complet en chunks
        
        Args:
            document: Document avec 'text' et 'metadata'
            
        Returns:
            Liste des chunks du document
        """
        text = document.get("text", "")
        metadata = document.get("metadata", {})
        
        # Découper le texte
        chunks = self.text_splitter.split_text(text)
        
        # Ajouter le numéro de page approximatif à chaque chunk
        total_pages = metadata.get("total_pages", 1)
        text_length = len(text)
        
        for i, chunk in enumerate(chunks):
            # Calculer la position relative du chunk dans le texte
            chunk_start = text.find(chunk)
            if chunk_start == -1:
                chunk_start = 0
            
            # Estimer le numéro de page approximatif
            relative_position = chunk_start / text_length if text_length > 0 else 0
            estimated_page = max(1, min(total_pages, int(relative_position * total_pages) + 1))
            
            # Créer les métadonnées du chunk
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": i,
                "estimated_page": estimated_page,
                "chunk_size": len(chunk)
            })
            
            chunks[i] = {
                "text": chunk,
                "metadata": chunk_metadata
            }
        
        logger.info(f"Texte découpé en {len(chunks)} chunks")
        return chunks
    
    def filter_chunks(self, chunks: list, min_length: int = 50) -> list:
        """
        Filtre les chunks selon des critères de qualité
        
        Args:
            chunks: Liste des chunks à filtrer
            min_length: Longueur minimale d'un chunk
            
        Returns:
            Liste des chunks filtrés
        """
        filtered_chunks = []
        
        for chunk in chunks:
            text = chunk.get("text", "").strip()
            
            # Ignorer les chunks trop courts
            if len(text) < min_length:
                continue
            
            # Ignorer les chunks qui ne contiennent que des espaces ou caractères spéciaux
            if not any(c.isalnum() for c in text):
                continue
            
            filtered_chunks.append(chunk)
        
        return filtered_chunks 