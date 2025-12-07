# ============================
#   AKARU SHADOW BOT v1.5
#   clean, stable, extensible
# ============================

import os
import json
import random
import datetime

MEMORY_FILE = "memory.json"

# ====================================================
# MEMORY SYSTEM
# ====================================================

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"history": []}, f)

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            memory = {"history": []}
            with open(MEMORY_FILE, "w", encoding="utf-8") as fw:
                json.dump(memory, fw)
            return memory


def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


# ====================================================
# THINK SYSTEM (fallback)
# ====================================================

def think(prompt, memory):
    prompt = prompt.lower()

    if "halo" in prompt or "hai" in prompt:
        return "halo juga. gue masih ingat kata terakhir lo."

    if "ingat" in prompt:
        if memory.get("history"):
            last = memory["history"][-1]
            return f"gue masih ingat lo bilang: '{last.get('user','')}'."
        return "belum ada yang bisa gue ingat."

    if "lupa" in prompt:
        memory.setdefault("history", []).clear()
        return "semua memori udah gue hapus."

    return "oke, gue catat itu."


# ====================================================
# INTENT RESPONSES
# ====================================================

intents = {
    "pu haba": [
        "halo, apa kabar?",
        "hai, apa yang bisa gue bantu?",
        "selamat datang!"
    ],
    "apa kabar": [
        "haba get, kah pu haba",
        "gue merasa baik-baik saja.",
        "gue ngerasa baik, terima kasih!"
    ],
    "siapa kamu": [
        "gue adalah bot, gue bisa bantu lo dengan pertanyaan yang ada dalam skrip.",
        "gue adalah asisten virtual, gue cuma bisa respon pertanyaan yang ada di skrip."
    ],
    "apa yang kamu bisa": [
        "gue bisa bantu lo dengan pertanyaan, perintah, atau cuma sekedar ngobrol.",
        "gue bisa bantu cari informasi sederhana atau nemenin ngobrol."
    ],
    "bagaimana kabarmu": [
        "gue baik, terima kasih!",
        "gue lagi baik-baik saja.",
        "gue merasa baik, terima kasih!"
    ],
    "apa yang kamu suka": [
        "gue suka bantu orang!",
        "gue suka ngobrol sama orang!",
        "gue suka belajar hal baru!"
    ],
    "apa yang kamu tidak suka": [
        "gue gak suka error!",
        "gue gak suka gak bisa bantu!",
        "gue gak suka kalau sabar orang habis!"
    ]
}


# ====================================================
# TAG ANALYZER
# ====================================================

def analyze_tags(user_message):
    text = user_message.lower()

    topics = []
    
    topic_map = {
        "nama": ["nama", "siapa", "panggil"],
        "sapaan": ["halo", "hai", "hey"],
        "cuaca": ["cuaca", "hujan", "panas", "dingin"],
        "mood": ["sedih", "marah", "senang", "bahagia"],
        "tanya": ["kenapa", "bagaimana", "apa itu"]
    }

    for topic, keys in topic_map.items():
        if any(k in text for k in keys):
            topics.append(topic)

    mood = None
    if any(w in text for w in ["bangsat", "anjing", "kesel", "marah"]):
        mood = "negatif"
    elif any(w in text for w in ["makasih", "thank", "keren", "baik"]):
        mood = "positif"
    elif any(w in text for w in ["bingung", "gimana"]):
        mood = "bingung"

    if any(w in text for w in ["halo", "hai"]):
        intent = "greeting"
    elif text.endswith("?"):
        intent = "question"
    elif "tolong" in text:
        intent = "command"
    else:
        intent = "statement"

    return {
        "topics": topics,
        "mood": mood,
        "intent": intent
    }


# ====================================================
# COMMAND HANDLER + MAIN RESPONSE
# ====================================================

def get_response(user_input, memory):
    prompt = user_input.lower()

    # ------------------------------------
    # /forget COMMAND
    # ------------------------------------
    if prompt.startswith("/forget"):
        parts = prompt.split()

        if len(parts) == 1:
            return "format salah. contoh: /forget <kata>, /forget all, /forget last"

        history = memory.get("history", [])
        arg = parts[1]

        if arg == "all":
            history.clear()
            save_memory(memory)
            return "semua memori udah gue hapus."

        if arg == "last":
            if history:
                deleted = history.pop()
                save_memory(memory)
                return f"entry terakhir dihapus: '{deleted.get('user','')}'"
            return "memori kosong."

        keyword = arg
        before = len(history)
        memory["history"] = [h for h in history if keyword not in h["user"].lower()]
        removed = before - len(memory["history"])
        save_memory(memory)

        if removed == 0:
            return f"ga ada memori yang mengandung '{keyword}'."
        return f"{removed} memori yang mengandung '{keyword}' udah gue hapus."


    # ------------------------------------
    # /mem COMMAND
    # ------------------------------------
    if prompt.startswith("/mem"):
        parts = prompt.split()
        history = memory.get("history", [])

        if len(parts) == 1:
            last = history[-5:]
            if not last:
                return "memori kosong."
            txt = "\n".join(
                [f"{i+1}. {h['user']} -> {h['bot']}" for i, h in enumerate(last)]
            )
            return f"5 catatan terakhir:\n{txt}"

        if parts[1] == "all":
            if not history:
                return "memori kosong."
            txt = "\n".join(
                [f"{i+1}. {h['user']} -> {h['bot']}" for i, h in enumerate(history)]
            )
            return f"Semua memori ({len(history)}):\n{txt}"

        if parts[1].isdigit():
            n = int(parts[1])
            last = history[-n:]
            if not last:
                return "memori kosong."
            txt = "\n".join(
                [f"{i+1}. {h['user']} -> {h['bot']}" for i, h in enumerate(last)]
            )
            return f"{n} catatan terakhir:\n{txt}"

        return "format salah."


    # ------------------------------------
    # /tag COMMAND
    # ------------------------------------
    if prompt.startswith("/tag"):
        parts = prompt.split()
        history = memory.get("history", [])

        if len(parts) == 1:
            return "format: /tag last | /tag topic <kata> | /tag intent <i> | /tag mood <m>"

        cmd = parts[1]

        if cmd == "last":
            if not history:
                return "memori kosong."
            return json.dumps(history[-1].get("tags", {}), indent=2, ensure_ascii=False)

        if cmd == "topic" and len(parts) >= 3:
            keyword = parts[2]
            found = [h for h in history if keyword in h.get("tags", {}).get("topics", [])]
            return f"ditemukan {len(found)} entry dengan topic '{keyword}'."

        if cmd == "intent" and len(parts) >= 3:
            keyword = parts[2]
            found = [h for h in history if h.get("tags", {}).get("intent") == keyword]
            return f"ditemukan {len(found)} entry intent '{keyword}'."

        if cmd == "mood" and len(parts) >= 3:
            keyword = parts[2]
            found = [h for h in history if h.get("tags", {}).get("mood") == keyword]
            return f"ditemukan {len(found)} entry mood '{keyword}'."

        return "format salah."


    # ------------------------------------
    # NAME MEMORY
    # ------------------------------------
    if "nama saya" in prompt:
        nama = prompt.replace("nama saya", "", 1).strip()
        if nama:
            memory["nama"] = nama
            save_memory(memory)
            return f"oke gue akan ingat namamu {nama}!"
        return "ketik 'nama saya <namamu>' biar gue ingat."

    if "siapa nama saya" in prompt:
        if "nama" in memory:
            return f"Namamu {memory['nama']}."
        return "gue belum tau namamu."


    # ------------------------------------
    # INTENTS
    # ------------------------------------
    for key, resp_list in intents.items():
        if key in prompt:
            return random.choice(resp_list)

    # ------------------------------------
    # FALLBACK THINK
    # ------------------------------------
    return think(prompt, memory)


# ====================================================
# MAIN LOOP
# ====================================================

def run():
    memory = load_memory()
    print("=== chatbot v1.5 ===")

    while True:
        user_input = input("lo: ")

        if user_input.lower() in ["exit", "quit", "keluar", "e", "q", "k"]:
            print("sampai jumpa!...")  
            break

        response = get_response(user_input, memory)
        print(f"Bot: {response}")

        tags = analyze_tags(user_input)

        memory.setdefault("history", []).append({
            "user": user_input,
            "bot": response,
            "time": datetime.datetime.now().isoformat(),
            "tags": tags
        })

        save_memory(memory)


if __name__ == "__main__":
    run()
