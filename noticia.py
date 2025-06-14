import requests
from bs4 import BeautifulSoup
import os
import urllib3
import smtplib
from email.mime.text import MIMEText

# Ignorar alertas de certificado SSL (caso use rede com proxy)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# CONFIGURAÇÕES DO E-MAIL (Gmail)
EMAIL_REMETENTE = "brunoconsoli96@gmail.com"
SENHA = "juqw ouoy edsl vqnz"  # Use uma senha de app do Gmail (não a senha da conta)
EMAILS_DESTINO = ["bruno.consoli@telefonica.com"]
SMTP_SERVIDOR = "smtp.gmail.com"
SMTP_PORTA = 587

# URLs das páginas e arquivo de controle
URLS = [
    "https://www.reformatributaria.com/category/governo/",
    "https://www.reformatributaria.com/category/brasil/",
    "https://www.reformatributaria.com/category/opiniao/",
    "https://www.reformatributaria.com/category/institucional/",
    "https://www.reformatributaria.com/category/educacao/",
    "https://www.reformatributaria.com/category/economia/",
    "https://www.reformatributaria.com/category/negocios/",
    "https://www.reformatributaria.com/category/tax-capital/",
]
ARQUIVO_ENVIADOS = "noticias_enviadas.txt"

# Palavras-chave para filtro (em minúsculas)
KEYWORDS = ["reforma", "ibs", "cbs", "roit"]

# Carregar links já enviados
if os.path.exists(ARQUIVO_ENVIADOS):
    with open(ARQUIVO_ENVIADOS, "r", encoding="utf-8") as f:
        links_enviados = set(l.strip() for l in f.readlines())
else:
    links_enviados = set()

novas_noticias = []

for URL in URLS:
    try:
        res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, verify=False, timeout=30)
        soup = BeautifulSoup(res.text, "html.parser")

        for a in soup.find_all("a", href=True):
            titulo = a.get_text(strip=True)
            link = a["href"]
            titulo_lower = titulo.lower()
            if any(k in titulo_lower for k in KEYWORDS) and link not in links_enviados:
                # Pegar os dois primeiros parágrafos da notícia no link
                try:
                    res_noticia = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, verify=False, timeout=30)
                    soup_noticia = BeautifulSoup(res_noticia.text, "html.parser")
                    ps = soup_noticia.find_all("p")
                    if len(ps) >= 2:
                        resumo = ps[0].get_text(strip=True) + " " + ps[1].get_text(strip=True)
                    elif len(ps) == 1:
                        resumo = ps[0].get_text(strip=True)
                    else:
                        resumo = "Resumo não disponível."
                except Exception:
                    resumo = "Resumo não disponível."

                novas_noticias.append((titulo, link, resumo))
    except Exception as e:
        print(f"❌ Erro ao acessar {URL}: {e}")

# Se houver novas, enviar por e-mail
if novas_noticias:
    corpo_html = "<h2>Novas notícias sobre Reforma Tributária, IBS e CBS</h2><ul>"
    for titulo, link, resumo in novas_noticias:
        corpo_html += f"<li><a href='{link}'>{titulo}</a><br><p>{resumo}</p></li><br>"
    corpo_html += "</ul>"

    msg = MIMEText(corpo_html, "html")
    msg["Subject"] = "Novas notícias sobre Reforma Tributária, IBS e CBS"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = ", ".join(EMAILS_DESTINO)

    try:
        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA) as server:
            server.starttls()
            server.login(EMAIL_REMETENTE, SENHA)
            server.sendmail(EMAIL_REMETENTE, EMAILS_DESTINO, msg.as_string())
        print("✅ E-mail enviado com sucesso!")

        with open(ARQUIVO_ENVIADOS, "a", encoding="utf-8") as f:
            for _, link, _ in novas_noticias:
                f.write(link + "\n")
    except Exception as e:
        print("❌ Erro ao enviar e-mail:", e)
else:
    print("Nenhuma nova notícia encontrada com as palavras-chave.")
