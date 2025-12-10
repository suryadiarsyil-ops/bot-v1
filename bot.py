# ============================
#   AKARU SHADOW BOT v2.0
#   Modular, Contextual, Scalable
# ============================

import os
import json
import random
import datetime

# --- KONFIGURASI ---
MEMORY_FILE = "memory.json"

# ====================================================
# A. MEMORY SYSTEM
# ====================================================

def load_memory():
    """Memuat memori dari file atau membuat struktur default jika tidak ada."""
    if not os.path.exists(MEMORY_FILE):
        # Buat file memory awal jika belum ada
        memory = {"history": [], "nama": "User"}
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        return memory

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Handle corrupted file
            print("[WARN] Memory file corrupted. Resetting memory.")
            memory = {"history": [], "nama": "User"}
            with open(MEMORY_FILE, "w", encoding="utf-8") as fw:
                json.dump(memory, fw, indent=2, ensure_ascii=False)
            return memory


def save_memory(memory):
    """Menyimpan struktur memori ke file."""
    # Gunakan ensure_ascii=False untuk support karakter non-ASCII (e.g., Bahasa Indonesia)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)


# ====================================================
# B. TAG ANALYZER (Diperluas untuk Waktu & Cuaca)
# ====================================================

def analyze_tags(user_message):
    """Menganalisis pesan pengguna untuk mendapatkan topik, mood, dan intent."""
    text = user_message.lower()

    topics = []
    
    # Perluasan Topik untuk Contextual Services
    topic_map = {
        "nama": ["nama", "siapa", "panggil"],
        "sapaan": ["halo", "hai", "hey"],
        "cuaca": ["cuaca", "hujan", "panas", "dingin", "suhu"],
        "waktu": ["jam", "tanggal", "sekarang", "hari apa", "pukul"], # New Topic
        "mood": ["sedih", "marah", "senang", "bahagia"],
        "tanya": ["kenapa", "bagaimana", "apa itu"]
    }

    for topic, keys in topic_map.items():
        if any(k in text for k in keys):
            topics.append(topic)

    # Mood (tetap sama)
    mood = None
    if any(w in text for w in ["bangsat", "anjing", "kesel", "marah"]):
        mood = "negatif"
    elif any(w in text for w in ["makasih", "thank", "keren", "baik"]):
        mood = "positif"
    elif any(w in text for w in ["bingung", "gimana"]):
        mood = "bingung"

    # Intent (tetap sama)
    if any(w in text for w in ["halo", "hai"]):
        intent = "greeting"
    elif text.endswith("?"):
        intent = "question"
    elif "tolong" in text or any(c in text for c in ["hapus", "catat", "cari"]):
        intent = "command"
    else:
        intent = "statement"

    return {
        "topics": topics,
        "mood": mood,
        "intent": intent
    }

# ====================================================
# C. INTENT RESPONSES & FALLBACK
# ====================================================

# Intent Responses (tetap dipertahankan untuk respon cepat)
INTENTS = {
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
        "gue adalah Akara Shadow Bot, gue bisa bantu lo dengan pertanyaan dan command yang tersedia.",
        "gue adalah asisten virtual, fokus gue: efisiensi. Lo bisa panggil gue Akara."
    ],
    "apa yang kamu bisa": [
        "gue bisa atur memori lo, menganalisis tag, dan menjawab pertanyaan sederhana. Ketik `/help` untuk command."
    ],
    "terima kasih": [
        "sama-sama. Ada lagi yang bisa gue *leverage*?",
        "terima kasih kembali. Jangan sungkan.",
        "oke, dicatat."
    ]
}

def think(prompt, memory):
    """Logika Fallback / Default."""
    prompt = prompt.lower()
    
    # Fallback yang lebih cerdas (menggunakan memori)
    if any(w in prompt for w in ["siapa", "apa"]):
        return "pertanyaan lo terlalu luas. Coba pakai `/mem` atau tanya tentang 'waktu' atau 'cuaca'..."

    # Fallback default
    return "oke, gue catat itu. Tapi kayaknya ini di luar skrip utama gue."


# ====================================================
# D. CONTEXTUAL SERVICES (MODULARITAS FUNGSI BARU)
# ====================================================

# D.1. Time Service
def get_time_response(tags):
    """Menghasilkan respon berdasarkan topik 'waktu'."""
    now = datetime.datetime.now()
    
    if "jam" in tags["topics"] or "pukul" in tags["topics"]:
        return f"Waktu sekarang adalah {now.strftime('%H:%M:%S')} WIB."
    
    if "tanggal" in tags["topics"] or "hari apa" in tags["topics"]:
        return f"Hari ini adalah {now.strftime('%A, %d %B %Y')}."
    
    return f"Informasi waktu lengkap: {now.strftime('%A, %d %B %Y, %H:%M:%S')} WIB."

# D.2. Weather Service (Mock)
def get_weather_response(tags):
    """Menghasilkan respon cuaca (saat ini masih mock / placeholder)."""
    # Placeholder: Di masa depan, di sini lo integrasikan API Cuaca
    city = "Jakarta" 
    
    if "suhu" in tags["topics"]:
        return f"Mock: Suhu di {city} saat ini 28°C. Data ini belum real time."
    
    if "hujan" in tags["topics"]:
        return f"Mock: Tidak ada potensi hujan di {city} dalam 3 jam ke depan. Data ini belum real time."

    return f"Mock: Cuaca di {city} saat ini cerah berawan. Butuh integrasi API Cuaca real time."


# ====================================================
# E. COMMAND HANDLERS (Implementasi Command Pattern)
# ====================================================

def handle_forget_command(user_input, memory):
    """Handler untuk command /forget."""
    parts = user_input.lower().split()

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

    # Forget by keyword
    keyword = arg
    before = len(history)
    memory["history"] = [h for h in history if keyword not in h["user"].lower()]
    removed = before - len(memory["history"])
    save_memory(memory)

    if removed == 0:
        return f"ga ada memori yang mengandung '{keyword}'."
    return f"{removed} memori yang mengandung '{keyword}' udah gue hapus."

def handle_mem_command(user_input, memory):
    """Handler untuk command /mem (menampilkan memori)."""
    parts = user_input.lower().split()
    history = memory.get("history", [])

    if len(parts) == 1:
        n = 5
        last = history[-n:]
    elif parts[1] == "all":
        last = history
        n = len(history)
    elif parts[1].isdigit():
        n = int(parts[1])
        last = history[-n:]
    else:
        return "format salah. Contoh: /mem, /mem all, /mem 10"

    if not last:
        return "memori kosong."
        
    txt = "\n".join(
        [f"{i+1}. {h['user']} -> {h['bot']}" for i, h in enumerate(last)]
    )
    return f"{min(n, len(history))} catatan terakhir:\n{txt}"

def handle_tag_command(user_input, memory):
    """Handler untuk command /tag (menganalisis tag di memori)."""
    parts = user_input.lower().split()
    history = memory.get("history", [])

    if len(parts) == 1:
        return "format: /tag last | /tag topic <kata> | /tag intent <i> | /tag mood <m>"

    cmd = parts[1]

    if cmd == "last":
        if not history:
            return "memori kosong."
        # Tampilkan dalam format JSON yang rapi
        return "Tag entry terakhir:\n" + json.dumps(history[-1].get("tags", {}), indent=2, ensure_ascii=False)

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

def handle_help_command(user_input, memory):
    """Handler untuk command /help."""
    commands = [
        "/help : Menampilkan daftar command ini.",
        "/mem [n/all] : Menampilkan n catatan memori terakhir (default 5) atau semua.",
        "/forget [kata/all/last] : Menghapus memori berdasarkan kata kunci atau semua/terakhir.",
        "/tag [last/topic/intent/mood] : Menganalisis dan mencari memori berdasarkan tag.",
        "nama saya <nama> : Bot akan mengingat namamu."
    ]
    return "Daftar Command Akara Bot:\n" + "\n".join(commands)


# F. COMMAND REGISTRY (Central Routing Point)
COMMAND_REGISTRY = {
    "/forget": handle_forget_command, 
    "/mem": handle_mem_command,
    "/tag": handle_tag_command,
    "/help": handle_help_command,
}

# ====================================================
# G. MAIN RESPONSE ROUTER (THE CLEAN CORE)
# ====================================================

def get_response(user_input, memory):
    """Fungsi utama yang menentukan respon bot."""
    prompt = user_input.lower()

    # ------------------------------------
    # 1. COMMAND ROUTING (Prioritas Tertinggi)
    # ------------------------------------
    if prompt.startswith("/"):
        command_key = prompt.split()[0]
        if command_key in COMMAND_REGISTRY:
            return COMMAND_REGISTRY[command_key](user_input, memory)
        return f"Command tidak dikenal: {command_key}. Coba `/help`."


    # ------------------------------------
    # 2. NAME MEMORY (Prioritas Tinggi)
    # ------------------------------------
    if "nama saya" in prompt:
        nama = prompt.replace("nama saya", "", 1).strip()
        if nama:
            memory["nama"] = nama
            save_memory(memory)
            return f"oke gue akan ingat namamu {nama}!"
        return "ketik 'nama saya <namamu>' biar gue ingat."

    if "siapa nama saya" in prompt or ("siapa" in prompt and "nama" in prompt):
        if "nama" in memory and memory["nama"] != "User":
            return f"Namamu {memory['nama']}."
        return "gue belum tau namamu. Ketik 'nama saya <namamu>'."


    # ------------------------------------
    # 3. CONTEXTUAL SERVICE ROUTING (THE NEW LOGIC)
    # ------------------------------------
    tags = analyze_tags(user_input)

    if "waktu" in tags["topics"]:
        return get_time_response(tags)

    if "cuaca" in tags["topics"]:
        # Lo bisa menambahkan logic pengecekan nama kota dari input di sini
        return get_weather_response(tags)


    # ------------------------------------
    # 4. INTENT HARDCODE FALLBACK
    # ------------------------------------
    for key, resp_list in INTENTS.items():
        if key in prompt:
            return random.choice(resp_list)


    # ------------------------------------
    # 5. FALLBACK THINK
    # ------------------------------------
    return think(prompt, memory)


# ====================================================
# H. MAIN LOOP
# ====================================================

def run():
    memory = load_memory()
    # Menggunakan nama pengguna yang tersimpan jika ada
    user_name = memory.get("nama", "User") 
    print("====================================")
    print("      === AKARU SHADOW BOT v2.0 ===")
    print("====================================")
    print("Ketentuan: Ketik `/help` untuk daftar command.")

    while True:
        # Menggunakan nama pengguna untuk prompt yang lebih personal
        user_input = input(f"{user_name}: ")

        if user_input.lower() in ["exit", "quit", "keluar", "e", "q", "k"]:
            print("Akara Bot: sampai jumpa!...")  
            break

        response = get_response(user_input, memory)
        print(f"Bot: {response}")

        # Update nama pengguna jika diubah dalam get_response
        user_name = memory.get("nama", "User")
        
        # Simpan interaksi ke History (termasuk tags)
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
