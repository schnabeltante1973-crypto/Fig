# Fig – Discord-Bot

Fig ist ein deutschsprachiger Discord-Charakter: eine dunkelorangene Walnuss mit Armen und Beinen, mit einer intelligenten, sarkastischen und vor allem selbstironischen Persönlichkeit.

## Funktionen

- `/fig text:...` – Fig eine Frage stellen oder mit ihm chatten
- `/fig aktion:Sitzen` – Fig führt eine vorbereitete Aktion aus
- `@Fig ...` – Fig antwortet auf direkte Erwähnungen
- Keine Antworten auf gewöhnliche Nachrichten ohne Erwähnung
- Begrenzter Gesprächskontext pro Nutzer und Kanal (nur im Arbeitsspeicher)
- Lokale GIF-Zuordnung über `gifs.json`

## Voraussetzungen

- Python 3.10 oder neuer
- Ein Discord-Bot im Discord Developer Portal
- Ein OpenAI API-Key für KI-Antworten
- Internetverbindung für Discord und die KI-Schnittstelle

## Installation

1. Entpacke den Projektordner.
2. Öffne ein Terminal im Ordner.
3. Installiere Abhängigkeiten:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Kopiere `.env.example` zu `.env`.
5. Trage `DISCORD_TOKEN` und `OPENAI_API_KEY` in `.env` ein.
6. Aktiviere im Discord Developer Portal unter **Bot → Privileged Gateway Intents** den **Message Content Intent**.
7. Lade den Bot über den OAuth2-URL-Generator mit den Scopes `bot` und `applications.commands` auf deinen Server ein. Er braucht mindestens die Berechtigungen **View Channels**, **Send Messages**, **Read Message History** und **Attach Files**.
8. Starte ihn:

   ```bash
   python bot.py
   ```

Die Slash-Befehle werden beim Start synchronisiert. Es kann kurz dauern, bis Discord sie überall anzeigt.

## Eigene GIFs hinzufügen

Lege deine GIF-Dateien in den Ordner `gifs/` und passe die Dateipfade in `gifs.json` an. Beispiel:

```json
"sit": {
  "file": "gifs/sitzen.gif",
  "caption": "Na gut. Ich setze mich."
}
```

Die GIF-Sammlung ist absichtlich nicht über Discord-Befehle bearbeitbar. Normale Mitglieder können keine GIFs hochladen oder Einträge ändern. Wer Zugriff auf die Bot-Dateien bzw. den Server hat, kann die Sammlung technisch verändern – sichere deshalb den Server und die Zugangsdaten.

## Hinweise

- Der Bot speichert den Gesprächsverlauf nur vorübergehend im RAM. Beim Neustart wird er gelöscht.
- Die KI-Antworten benötigen einen OpenAI API-Key; API-Nutzung kann Kosten verursachen.
- Die GIFs sind noch Platzhalter. Die Dateien `sitzen.gif`, `stehen.gif` usw. müssen von dir bereitgestellt werden.
- `/fig` ohne Text oder Aktion zeigt eine kurze Hilfe. Nutze z. B. `/fig text:Hallo Fig!`.
- Fig antwortet auf Nachrichten nur, wenn er direkt erwähnt wird.
- Teile niemals deinen Discord-Token oder API-Key. Wenn ein Token versehentlich veröffentlicht wurde, rotiere ihn im jeweiligen Entwicklerportal.
