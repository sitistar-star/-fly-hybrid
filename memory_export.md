Fly.io hybrid: hermes-agent-cloud.fly.dev (ams, 1x shared-512MB, $3.19/мес). API сервер работает /health → ok. Бот @Aleksgipnobot (8573027399) занят локальным gateway (Scheduled Task). Нужен второй бот для облака или группа с обоими. Trial без карты — машины гаснут через 5 мин. API_SERVER_KEY установлен. Проект: ~/fly-hybrid/.
§
User wants the agent to auto-restart when it gets stuck/stalled/stopped. "перезагружайся когда остановка" — restart on stall.
§
Web toolset configured: search_backend=tavily, extract_backend=firecrawl. API keys still needed (TAVILY_API_KEY, FIRECRAWL_API_KEY). DuckDuckGo search skill installed as fallback.
§
OneDrive sync: desktop at C:\Users\sitis\OneDrive\Desktop, NOT C:\Users\sitis\Desktop. AntiGravity (VS Code fork) at C:\Users\sitis\AppData\Local\Programs\Antigravity. VoiceBridge at C:\Users\sitis\voicebridge (port 10999, Ctrl+Shift+V push-to-talk).
§
User directive: "никогда не останавливайся, доделывай до конца и возобновляй работу" — always finish tasks completely, never stop mid-way.
§
Google Drive настроен через rclone (полный доступ scope=drive). Токен хранится в C:\Users\sitis\AppData\Local\Temp\rclone-full.conf (секция [gdrive-full]). Для быстрой загрузки: /tmp/rclone.exe copy <file> gdrive-full: --config /tmp/rclone-full.conf. Для публичного доступа: через Python Google Drive API. Файлы на Google Drive: огромная коллекция книг по медицине/акупунктуре/кинезиологии, карты Полтавской обл., Android APK, доки. Не удалять ничего без разрешения.
§
Obsidian v1.12.7 установлен. Vaults: C:\Users\sitis\OneDrive\Документы\Obsidian Vault (основной), C:\Users\sitis\OneDrive\Desktop\гермес\нермес (активный, открыт). Obsidian аккаунт: sitistar@gmail.com, пароль обновлён, вход выполнен.
§
User prefers calm/muted UI colors on web pages: warm dark bg #1a1b2e, peach accent #d4a373, sage green #9abb8a, muted text. Font: Inter + Literata for body. No harsh contrast or neon.
§
Android APK сборка настроена: JDK 21 (C:\Users\sitis\jdk-21.0.6+7), Android SDK (C:\Users\sitis\Android\Sdk), Capacitor проект health-app-capacitor. Команда: cd health-app-capacitor/android && ./gradlew assembleDebug.