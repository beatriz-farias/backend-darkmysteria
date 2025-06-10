import os
from groq_utils import get_groq_raw_interpretation
from riddles import get_next_riddle_id, get_riddle_by_id
from utils import audio_to_text, text_to_audio_bytes

def interpret_question_with_ai(
    audio_file_path: str,
    current_riddle_id: int, # NOVO: ID da charada atual
    player_intent: str      # NOVO: 'ask_question' ou 'say_answer'
) -> dict:
    """
    Processa a entrada de áudio do jogador com base na sua intenção (pergunta ou resposta).
    Retorna um dicionário com o resultado do jogo (resposta de texto, áudio, nova charada, etc.).
    """
    user_question_text = audio_to_text(audio_file_path)

    if not user_question_text:
        error_msg = "Não consegui entender sua pergunta no áudio. Por favor, tente novamente."
        error_audio = text_to_audio_bytes(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "audio_base64": error_audio
        }

    riddle_data = get_riddle_by_id(current_riddle_id)
    if not riddle_data:
        error_msg = "Erro: Charada não encontrada no sistema. Por favor, reinicie o jogo."
        error_audio = text_to_audio_bytes(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "audio_base64": error_audio
        }

    # --- Lógica principal baseada na intenção do jogador ---
    if player_intent == 'ask_question':
        groq_raw_response = get_groq_raw_interpretation(user_question_text, riddle_data, player_intent)
        
        final_answer_text: str
        if groq_raw_response == "GROQ_API_ERROR":
            final_answer_text = "Desculpe, a entidade está ocupada no momento. Tente novamente."
        elif "sim" in groq_raw_response:
            final_answer_text = "Sim"
        elif "não é uma pergunta sim/não" in groq_raw_response or "não é uma pergunta de sim ou não" in groq_raw_response:
            final_answer_text = "Não é uma pergunta sim/não"
        elif "não" in groq_raw_response:
            final_answer_text = "Não"
        elif "irrelevante" in groq_raw_response:
            final_answer_text = "Irrelevante"
        else:
            print(f"Atenção: Resposta inesperada do Groq (pergunta): '{groq_raw_response}'. Retornando 'Irrelevante'.")
            final_answer_text = "Irrelevante"

        final_answer_audio = text_to_audio_bytes(f"A Entidade responde: {final_answer_text}")
        return {
            "status": "success",
            "type": "question_response",
            "message": final_answer_text,
            "audio_base64": final_answer_audio,
            "current_riddle_id": current_riddle_id # Mantém o mesmo ID
        }

    elif player_intent == 'say_answer':
        # Para avaliação da resposta, primeiro tentamos uma correspondência exata para maior precisão
        player_answer_cleaned = user_question_text.strip().lower()
        correct_answer_cleaned = riddle_data['answer'].strip().lower()

        is_correct_local = (player_answer_cleaned == correct_answer_cleaned)

        # Opcional: Usar Groq para confirmação ou avaliação mais flexível
        # Se você quiser que o Groq seja o árbitro final, mesmo com variações.
        groq_raw_response = get_groq_raw_interpretation(user_question_text, riddle_data, player_intent)
        is_correct_by_ai = (groq_raw_response == 'correct')

        # Decide se a resposta é correta: prioriza correspondência exata, depois Groq se houver variação.
        correct = is_correct_local or is_correct_by_ai # Se uma for true, já é suficiente

        if correct:
            next_riddle_id = get_next_riddle_id(current_riddle_id)
            if next_riddle_id:
                next_riddle_data = get_riddle_by_id(next_riddle_id)
                response_text = "Parabéns! Você desvendou a charada. Agora, a próxima..."
                response_audio = text_to_audio_bytes(response_text)
                return {
                    "status": "success",
                    "type": "answer_evaluation",
                    "correct": True,
                    "message": response_text,
                    "audio_base64": response_audio,
                    "current_riddle_id": next_riddle_id, # Avança para a próxima charada
                    "next_riddle_text": next_riddle_data['text'] if next_riddle_data else None
                }
            else:
                response_text = "Parabéns! Você desvendou a última charada. A entidade está satisfeita... por enquanto."
                response_audio = text_to_audio_bytes(response_text)
                return {
                    "status": "success",
                    "type": "game_complete",
                    "message": response_text,
                    "audio_base64": response_audio,
                    "current_riddle_id": current_riddle_id
                }
        else:
            response_text = "Resposta incorreta. Tente novamente, a entidade não tolera erros."
            response_audio = text_to_audio_bytes(response_text)
            return {
                "status": "success",
                "type": "answer_evaluation",
                "correct": False,
                "message": response_text,
                "audio_base64": response_audio,
                "current_riddle_id": current_riddle_id # Permanece na mesma charada
            }
    else:
        error_msg = f"Intenção '{player_intent}' desconhecida para o processamento da IA."
        error_audio = text_to_audio_bytes(error_msg)
        return {
            "status": "error",
            "message": error_msg,
            "audio_base64": error_audio
        }

