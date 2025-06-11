import streamlit as st
import logging

logger = logging.getLogger(__name__)

class QAInterface:
    """Interface utilisateur pour l'assistant IA"""
    
    def __init__(self, rag_chain):
        """
        Initialise l'interface
        
        Args:
            rag_chain: Instance de RAGChain
        """
        self.rag_chain = rag_chain
        
        # Initialiser la session state
        if "qa_history" not in st.session_state:
            st.session_state.qa_history = []
    
    def run(self):
        """Lance l'interface principale"""
        st.set_page_config(
            page_title="DocSearch - Assistant IA",
            page_icon="📚",
            layout="wide"
        )
        
        # En-tête
        st.title("📚 DocSearch - Assistant IA de Lecture")
        st.markdown("---")
        
        # Interface principale
        self._main_interface()
        
        # Historique
        self.display_qa_history()
    
    def _main_interface(self):
        """Interface principale de question/réponse"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Zone de saisie de question
            question = st.text_area(
                "Posez votre question sur le document :",
                placeholder="Ex: De quoi parle ce document ? Quels sont les points clés ?",
                height=100
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("🔍 Poser la question", type="primary"):
                if question.strip():
                    self._process_question(question.strip())
                else:
                    st.warning("Veuillez saisir une question.")
        
        # Affichage de la dernière réponse
        if st.session_state.qa_history:
            latest_qa = st.session_state.qa_history[-1]
            self.display_qa_response(latest_qa)
    
    def _process_question(self, question: str):
        """Traite une question et affiche la réponse"""
        with st.spinner("🤔 L'assistant réfléchit..."):
            try:
                # Obtenir la réponse via la chaîne RAG
                result = self.rag_chain.ask_question(question)
                
                # Ajouter à l'historique
                qa_entry = {
                    "question": question,
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "timestamp": st.session_state.get("current_time", "Maintenant")
                }
                
                st.session_state.qa_history.append(qa_entry)
                
                # Recharger la page pour afficher la réponse
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur lors du traitement de votre question: {str(e)}")
                logger.error(f"Erreur dans l'interface: {e}")
    
    def display_qa_response(self, qa_entry: dict):
        """Affiche une réponse Q&A"""
        st.markdown("---")
        
        # Question
        st.markdown(f"**❓ Question :** {qa_entry['question']}")
        
        # Réponse
        st.markdown(f"**🤖 Réponse :**")
        st.write(qa_entry['answer'])
        
        # Sources
        if qa_entry.get('sources'):
            with st.expander("📄 Sources et citations"):
                for i, source in enumerate(qa_entry['sources'], 1):
                    st.markdown(f"**Source {i} :**")
                    st.markdown(f"- **Fichier :** {source.get('filename', 'Inconnu')}")
                    st.markdown(f"- **Page :** {source.get('page', 'N/A')}")
                    st.markdown(f"- **Extrait :** {source.get('text', '')}")
                    st.markdown("---")
    
    def display_qa_history(self):
        """Affiche l'historique des questions/réponses"""
        if st.session_state.qa_history:
            st.subheader("📚 Historique des Questions/Réponses")
            
            # Filtres
            col1, col2 = st.columns([2, 1])
            with col1:
                search_term = st.text_input("Rechercher dans l'historique", placeholder="Mot-clé...")
            with col2:
                if st.button("🗑️ Effacer l'historique"):
                    st.session_state.qa_history = []
                    st.rerun()
            
            # Affichage filtré
            filtered_history = self.filter_qa_history(search_term)
            
            for qa_entry in filtered_history:
                self.display_qa_response(qa_entry)
    
    def filter_qa_history(self, search_term: str) -> list:
        """Filtre l'historique selon un terme de recherche"""
        if not search_term:
            return st.session_state.qa_history
        
        filtered = []
        search_lower = search_term.lower()
        
        for qa in st.session_state.qa_history:
            if (search_lower in qa['question'].lower() or 
                search_lower in qa['answer'].lower()):
                filtered.append(qa)
        
        return filtered 