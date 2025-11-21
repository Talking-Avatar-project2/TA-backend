import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from contexts.chatbot_management.infrastructure.repositories.chatbot_repository import ChatbotRepository

# Test 1: Guardar varios mensajes
print("=" * 60)
print("TEST 1: Guardando mensajes...")
print("=" * 60)

user_id = "test_user_debug"

messages = [
    ("Hola, ¿cómo estás?", "(Neutra) Hola, estoy bien. ¿En qué puedo ayudarte?"),
    ("Estoy triste", "(Negativa) Lamento que te sientas así. ¿Quieres hablar sobre ello?"),
    ("Sí, gracias", "(Positiva) Estoy aquí para escucharte."),
]

for user_msg, bot_msg in messages:
    ChatbotRepository.save_message(user_msg, bot_msg, user_id)
    print(f"✅ Guardado: {user_msg[:30]}...")

# Test 2: Recuperar historial
print("\n" + "=" * 60)
print("TEST 2: Recuperando historial...")
print("=" * 60)

history = ChatbotRepository.get_conversation_history(user_id, limit=10)

print(f"\n📚 Total de mensajes recuperados: {len(history)}")

if len(history) == 0:
    print("❌ ERROR: No se recuperaron mensajes")
    print("   Posibles causas:")
    print("   1. orderBy requiere índice en Firestore")
    print("   2. user_id incorrecto")
    print("   3. Conversión de formato incorrecta")
else:
    print("✅ Mensajes recuperados correctamente:")
    for i, msg in enumerate(history):
        print(f"\n[{i}] Usuario: {msg.user_message}")
        print(f"    Bot: {msg.bot_response}")
        print(f"    Emoción: {msg.emotion_type}")
        print(f"    Timestamp: {msg.timestamp}")