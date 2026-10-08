import os
from openai import OpenAI

# المفتاح يتقرا من Environment variable - متحطش المفتاح في الكود
# set NVIDIA_API_KEY=... في الويندوز او حطه في ملف .env
api_key = os.getenv("NVIDIA_API_KEY")
if not api_key:
    print("ERROR: حط المفتاح الاول:")
    print('  set NVIDIA_API_KEY=nvapi-... (ويندوز cmd)')
    print('  او: $env:NVIDIA_API_KEY="nvapi-..." (باورشيل)')
    raise SystemExit(1)

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key,
)

# موديل مجاني وسريع على NVIDIA Build - غيره من https://build.nvidia.com/search
MODEL = "deepseek-ai/deepseek-v3.1"

messages = [
    {"role": "system", "content": "انت مساعد مفيد بترد بالعربي المصري المبسط."}
]

print(f"شغال على {MODEL} - اكتب 'خروج' عشان تطلع\n")
while True:
    q = input("انت: ").strip()
    if q in ("خروج", "exit", "quit"):
        break
    if not q:
        continue
    messages.append({"role": "user", "content": q})
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.6,
        max_tokens=1024,
    )
    ans = resp.choices[0].message.content
    print(f"\nالبوت: {ans}\n")
    messages.append({"role": "assistant", "content": ans})
