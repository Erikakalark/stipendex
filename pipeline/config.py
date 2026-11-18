"""Regler och listor som taggningen använder. Ändra här, inte i tag.py."""

# Lärosäten: kod -> (namn, regex för omnämnande i ändamål/c/o, ansökningsinfo)
UNIS = {
    "UU": {"name": "Uppsala universitet", "city": "uppsala",
           "rx": r"uppsala universitet|upsala universitet|universitetet i uppsala|uppsala akademiförvaltning|upsala akademi",
           "how": "Söks i Uppsala universitets stipendiesystem. Stora ansökningsomgången öppnar i början av varje termin.",
           "url": "https://www.uu.se/student/studentliv/studentekonomi/stipendier"},
    "SLU": {"name": "Sveriges lantbruksuniversitet", "city": "uppsala",
            "rx": r"\bslu\b|lantbruksuniversitet|ultuna|lantbrukshögskola|alnarp",
            "how": "Söks via SLU, oftast en gång per år via fakultetens stipendiekommitté.",
            "url": "https://student.slu.se/en/student-life/scholarships"},
    "LU": {"name": "Lunds universitet", "city": "lund",
           "rx": r"lunds universitet|lunds univ|universitetet i lund|lunds akademi|lund universit",
           "how": "Söks via Lunds universitets gemensamma ansökan för universitets- och nationsstipendier, i februari och september. En ansökan täcker alla stipendier du är behörig till.",
           "url": "https://www.lu.se/student/stipendier-dig-som-ar-student"},
    "SU": {"name": "Stockholms universitet", "city": "stockholm",
           "rx": r"stockholms universitet|stockholms högskola",
           "how": "Söks i Stockholms universitets gemensamma webbansökan för donationsstipendier, en gång per år. Perioden skiljer sig mellan fakulteterna.",
           "url": "https://www.su.se/utbildning/studera-vid-universitetet/stipendier"},
    "KTH": {"name": "KTH", "city": "stockholm",
            "rx": r"kungl(?:iga|\.)? tekniska högskolan|\bkth\b|tekniska högskolan i stockholm",
            "how": "Söks via KTH:s stipendieportal. De flesta KTH-stipendier delas ut en gång per år, många med ansökan 15 januari – 15 februari.",
            "url": "https://www.kth.se/student/stod/studier/stipendier"},
    "KI": {"name": "Karolinska institutet", "city": "stockholm",
           "rx": r"karolinska institut|mediko-kirurgisk",
           "how": "Söks via KI:s årliga utlysning av stiftelsestipendier eller enskilda utlysningar.",
           "url": "https://education.ki.se/the-karolinska-institutet-foundation-scholarships"},
    "GU": {"name": "Göteborgs universitet", "city": "goteborg",
           "rx": r"göteborgs universitet|göteborgs högskola|handelshögskolan i göteborg|sahlgrenska akademi",
           "how": "Söks i Göteborgs universitets webbaserade stipendiesystem. Stiftelserna har egna utlysningar under året.",
           "url": "https://studentportal.gu.se"},
    "CTH": {"name": "Chalmers", "city": "goteborg",
            "rx": r"chalmers",
            "how": "Söks via Chalmers stipendiesidor. Flera stipendier har ansökan över vintern.",
            "url": "https://www.chalmers.se/utbildning/dina-studier/planera-och-genomfora-studier/stipendier-for-studenter/"},
    "LIU": {"name": "Linköpings universitet", "city": "linkoping",
            "rx": r"linköpings universitet|universitetet i linköping|linköpings tekniska högskola",
            "how": "Kontakta Linköpings universitet eller institutionen om ansökan.", "url": "https://liu.se/"},
    "UMU": {"name": "Umeå universitet", "city": "umea",
            "rx": r"umeå universitet|universitetet i umeå",
            "how": "Stiftelserna lyser ut medel var för sig, ofta på universitetets webb.", "url": "https://www.umu.se/"},
    "MAU": {"name": "Malmö universitet", "city": "malmo",
            "rx": r"malmö universitet|malmö högskola|tandläkarhögskolan i malmö|lärarhögskolan i malmö",
            "how": "Se Malmö universitets stipendiesida, frågor till stipendier@mau.se.",
            "url": "https://student.mau.se/en/my-studies/scholarships"},
}

NATIONS = {
    "uppsala": {
        "Stockholms nation": r"stockholms?[ -]nation", "Uplands nation": r"up?p?lands?[ -]nation|upländing",
        "Gästrike-Hälsinge nation": r"gästrike|hälsinge[ -]?nation", "Östgöta nation": r"östgöt[a-z]*[ -]nation|östg\. nation",
        "Västgöta nation": r"västgöt[a-z]*[ -]nation", "Södermanlands-Nerikes nation": r"södermanlands?[- ]n[ae]rike|sörmlands?[- ]nation|nerikes nation",
        "Västmanlands-Dala nation": r"västmanlands?[- ]dala|vdala|dala[ -]nation", "Smålands nation": r"smålands?[ -]nation",
        "Göteborgs nation": r"göteborgs?[ -]nation", "Kalmar nation": r"kalmar[ -]nation", "Värmlands nation": r"värmlands?[ -]nation",
        "Norrlands nation": r"norrlands?[ -]nation|norrländska nation", "Gotlands nation": r"gotlands?[ -]nation",
    },
    "lund": {
        "Blekingska nationen": r"blekingsk[a-z]* nation", "Göteborgs nation": r"göteborgs?[ -]nation", "Hallands nation": r"hallands?[ -]nation",
        "Helsingkrona nation": r"helsingkrona|helsingborgs?-landskrona", "Kalmar nation": r"kalmar[ -]nation",
        "Kristianstads nation": r"kristianstads?[ -]nation", "Lunds nation": r"lunds?[ -]nation", "Malmö nation": r"malmö[ -]nation",
        "Sydskånska nationen": r"sydskånsk|södra skånsk", "Smålands nation": r"smålands?[ -]nation", "Västgöta nation": r"västgöt[a-z]* nation",
        "Värmlands nation": r"värmlands?[ -]nation", "Östgöta nation": r"östgöt[a-z]* nation",
    },
}
LUND_SKANSKA = ["Lunds nation", "Malmö nation", "Helsingkrona nation", "Kristianstads nation", "Sydskånska nationen"]
NATION_URL = {
    "Stockholms nation": "https://www.stocken.se", "Uplands nation": "https://uplandsnation.se", "Gästrike-Hälsinge nation": "https://ghnation.se",
    "Östgöta nation": "https://ostgotanation.se", "Västgöta nation": "https://vastgotanation.se", "Södermanlands-Nerikes nation": "https://www.snerikes.se/stipendier",
    "Västmanlands-Dala nation": "https://www.v-dala.se", "Smålands nation": "https://smalandsnation.com", "Göteborgs nation": "https://www.goteborgsnation.se",
    "Kalmar nation": "https://www.kalmarnation.se", "Värmlands nation": "https://www.varmlandsnation.se", "Norrlands nation": "https://www.norrlandsnation.se",
    "Gotlands nation": "https://www.gotlandsnation.se",
}

SUBJECTS = {
    "medicin": r"medicin|\bmed\.\s*(?:stud|kand|lic|fakult)|med\.,|läkar|kirurg|klinisk|patolog|psykiatri|cancer|sjukvård|vårdvetenskap|sjuksköterska|fysioterap|tandläk|odontolog",
    "farmaci": r"farmac|apotek|läkemedel",
    "juridik": r"jurid|\bjur\.|rättsvet|juris|jurist",
    "teologi": r"teolog|\bteol\.?|präst|religion|missions|bibel",
    "ekonomi": r"ekonomi|nationalekonomi|företagsekonomi|handel|statistik",
    "historia": r"histori|arkeolog|antikvar|fornminne|kulturarv|numismat",
    "språk": r"språkvet|språk|latin|grekisk|klassisk|filolog|lingvist|litteratur|semitisk|sanskrit|orientalisk|slavisk",
    "konst och musik": r"konst|musik|sång|körsång|orgel|tonkonst|teater|måleri|arkitektur|design|dans|film",
    "humaniora": r"hist\.-fil|humanist|humaniora|filosofi|estetik|idéhistori|etnolog|kulturvetenskap",
    "samhällsvetenskap": r"samhällsvet|statsvet|sociologi|kulturgeografi|pedagogik|psykologi|statskunskap|socialvetenskap|journalist|socialt arbete",
    "naturvetenskap": r"mat\.-nat|naturvetenskap|fysik|kemi|biolog|matematik|astronomi|geolog|botanik|zoolog|geovetenskap|meteorolog|ekolog",
    "teknik": r"teknik|teknisk|ingenjör|informationsteknolog|data(?:teknik|vetenskap)",
    "lantbruk och skog": r"lantbruk|jordbruk|skog|trädgård|husdjur|mejeri|agronom|hortonom|landsbygd|fiske|växtodling",
    "veterinär": r"veterinär|djursjuk|djurhälsa|hippolog",
    "miljö": r"miljö|naturvård|klimat|hållbar",
    "idrott": r"idrott|sport",
}

LEVELS = {
    "student": r"studer|student|stud\.|nationsmedlem|medlem(?:mar)? av .{0,30}nation|yngling|studier vid|studiestipend|grundutbildning|kandidat|lärjung",
    "doktorand": r"doktorand|forskarstud|forskarutbildning|licentiat|avhandling|disputation|doktorsgrad|docent",
    "forskare": r"forskare|vetenskapligt arbete|vetenskaplig verksamhet|vetenskapliga undersökning|vetenskapliga studier|forskning",
    "elev": r"\belev|skolungdom|gymnasi|läroverk|folkhögskol|realskol",
}

# Målgrupper för bidrag (icke-studenter)
AID = {
    "ekonomiskt behov": r"obemedl|behövande|mindre bemedl|medellös|fattig|ekonomiskt behov|svag ekonomi|ekonomisk hjälp|understöd åt",
    "äldre": r"åldring|äldre|ålderstigna|pensionär|gamla",
    "sjuka och funktionsnedsatta": r"sjuka|sjukdom|handikapp|funktionsnedsätt|invalid|rörelsehindr|blind|döv|konvalescen",
    "barn och familj": r"barn(?!barn)|änkor|änkling|ensamstående|mödrar|familj|föräldralös",
    "kultur": r"konstnär|författare|musiker|tonsättare|kulturutövare",
}

GAZ = ['Skåne', 'Blekinge', 'Halland', 'Småland', 'Öland', 'Gotland', 'Östergötland', 'Västergötland', 'Bohuslän', 'Dalsland', 'Värmland', 'Närke',
       'Södermanland', 'Uppland', 'Västmanland', 'Dalarna', 'Gästrikland', 'Hälsingland', 'Härjedalen', 'Jämtland', 'Medelpad', 'Ångermanland',
       'Västerbotten', 'Norrbotten', 'Lappland', 'Roslagen', 'Norrland', 'Finland', 'Norge', 'Danmark', 'Island', 'Estland',
       'Stockholm', 'Göteborg', 'Malmö', 'Linköping', 'Norrköping', 'Örebro', 'Västerås', 'Gävle', 'Sundsvall', 'Umeå', 'Luleå', 'Karlstad',
       'Jönköping', 'Växjö', 'Kalmar', 'Visby', 'Falun', 'Härnösand', 'Östersund', 'Nyköping', 'Eskilstuna', 'Enköping', 'Norrtälje', 'Sala',
       'Skara', 'Strängnäs', 'Västervik', 'Halmstad', 'Borås', 'Uddevalla', 'Kristianstad', 'Lund', 'Helsingborg', 'Hudiksvall', 'Söderhamn',
       'Bollnäs', 'Tierp', 'Östhammar', 'Uppsala', 'Sigtuna', 'Arboga', 'Köping', 'Avesta', 'Hedemora', 'Mora', 'Ludvika', 'Kiruna', 'Piteå',
       'Skellefteå', 'Örnsköldsvik', 'Motala', 'Mjölby', 'Vadstena', 'Lidköping', 'Mariestad', 'Trollhättan', 'Vänersborg', 'Arvika',
       'Kristinehamn', 'Filipstad', 'Vimmerby', 'Oskarshamn', 'Karlskrona', 'Ronneby', 'Ystad', 'Trelleborg', 'Landskrona', 'Varberg', 'Eksjö',
       'Nora', 'Askersund', 'Lindesberg', 'Fagersta', 'Trosa', 'Södertälje', 'Ängelholm', 'Hässleholm', 'Simrishamn', 'Kungsbacka', 'Alingsås',
       'Skövde', 'Falköping', 'Ulricehamn', 'Värnamo', 'Ljungby', 'Nässjö', 'Vetlanda', 'Borlänge', 'Sandviken', 'Kramfors', 'Sollefteå',
       'Boden', 'Haparanda', 'Gällivare', 'Lycksele']
DEMONYM = {'värmlänning': 'Värmland', 'smålänning': 'Småland', 'norrlänning': 'Norrland', 'upplänning': 'Uppland', 'upländing': 'Uppland',
           'gotlänning': 'Gotland', 'skåning': 'Skåne', 'dalkarl': 'Dalarna', 'hälsing': 'Hälsingland', 'gästrik': 'Gästrikland',
           'sörmlänning': 'Södermanland', 'närking': 'Närke', 'hallänning': 'Halland', 'blekinging': 'Blekinge', 'jämtlänning': 'Jämtland',
           'västerbottning': 'Västerbotten', 'norrbottning': 'Norrbotten', 'bohuslänning': 'Bohuslän', 'stockholmare': 'Stockholm'}
NORRLAND = ['Gästrikland', 'Hälsingland', 'Härjedalen', 'Jämtland', 'Medelpad', 'Ångermanland', 'Västerbotten', 'Norrbotten', 'Lappland']

# Val i profilformuläret (landskap m.m.)
LANDS_UI = ["Blekinge", "Bohuslän", "Dalarna", "Dalsland", "Gotland", "Gästrikland", "Halland", "Hälsingland", "Härjedalen", "Jämtland",
            "Lappland", "Medelpad", "Norrbotten", "Närke", "Skåne", "Småland", "Södermanland", "Uppland", "Värmland", "Västerbotten",
            "Västergötland", "Västmanland", "Ångermanland", "Öland", "Östergötland", "Stockholm", "Göteborg", "Malmö", "Finland", "Annat land"]
