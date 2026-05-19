# MobileWeb - Omron Status Monitor

Den här delen av projektet är själva **webbappen** (användargränssnittet) som du ser i din webbläsare eller mobil. 

Mobilappen hämtar ständigt den senaste statusen och eventuella felmeddelanden från Omron-robotarna. Den översätter sedan denna data till tydliga grafiska kort som visar om varje robot är PÅ eller AV, vad den gör just nu, och larmar direkt om något går fel (till exempel om en koppling bryts).

---

## (Front End)

Webbappen är byggd med modern webbteknik: **React**, **TypeScript** och **Tailwind CSS**. Om du vill ändra design, färger, animationer eller lägga till nya knappar och information på skärmen, är det dessa filer du ska titta på:

*   **`App.tsx`**: Detta är den i särklass viktigaste filen för utseendet. Här inne hittar du strukturen (som liknar HTML) som bygger upp statuskorten för robotarna. Här finns också logiken som bestämmer när en robot ska lysa grönt eller rött.
*   **`index.css`**: Här ligger grundinställningarna för Tailwind CSS. Det är också här du kan lägga in helt egen traditionell CSS om du skulle behöva det.
*   **`tailwind.config.js`**: Använd denna fil om du vill lägga till egna anpassade färgkoder, typsnitt eller ändra standardteman i Tailwind.

*(När du gör ändringar i Front End och vill bygga en färdig version för produktion, glöm inte att köra kommandot `npm run build` i denna mapp).*

---

## (Back End)

Den inbyggda backenden för den här specifika webbappen är skriven i **Python** med ramverket **Flask**. Om du vill ändra vilken data som appen har tillgång till, eller hur datan hämtas från databasen, ska du titta här:

*   **`mobile_web_server.py`**: Detta är motorn bakom kulisserna. Filen ansluter till TimescaleDB-databasen, skickar SQL-förfrågningar för att hämta de senaste robotstatusarna och felen. Den paketerar sedan ihop denna data och skapar en "API-länk" (`/api/Status_and_errors`) som Front End läser av var femte sekund.

Om du till exempel lägger till en ny typ av sensor på roboten och vill visa den i appen, måste du först ändra SQL-koden i `mobile_web_server.py` för att hämta datan, och sedan ändra i `App.tsx` för att rita ut den!