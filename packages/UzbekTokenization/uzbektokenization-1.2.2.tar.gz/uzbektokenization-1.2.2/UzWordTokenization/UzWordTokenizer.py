import re


def __division(tokens):
    new_tokens = []

    for token in tokens:
        # Separating characters at the beginning and end
        match = re.match(r'^(\W*)(.*?)(\W*)$', token)
        if match:
            start_punct, content, end_punct = match.groups()

            # If there are beginning and ending characters, they are added separately
            if start_punct:
                # If there are multiple characters at the beginning, they are separated separately
                if len(start_punct) > 1:
                    for char in start_punct:
                        new_tokens.append(char)
                else:
                    new_tokens.append(start_punct)
            if content:
                new_tokens.append(content)
            if end_punct:
                # If there are multiple characters at the ending, they are separated separately
                if len(end_punct) > 1:
                    for char in end_punct:
                        new_tokens.append(char)
                else:
                    new_tokens.append(end_punct)

    return new_tokens


def __gerund(tokens):
    # Save the original tokens to refer back to them later after transformations
    original_tokens = tokens

    tokens = [item.lower() for item in tokens]
    new_tokens = [original_tokens[0]]

    # Iterate over the tokens starting from the second token
    for i in range(1, len(tokens)):
        # Check if the previous token ends with '-(u)v' and the current token is one of the key words
        if tokens[i-1][-1] == 'v' and (tokens[i] in ['kerak', 'lozim', 'shart', 'darkor']):
            del new_tokens[len(new_tokens)-1]
            new_tokens.append(original_tokens[i-1] + ' ' + original_tokens[i])

        elif tokens[i-1][-2:] == 'sh' and (tokens[i] in ['kerak', 'lozim', 'shart', 'darkor']):
            del new_tokens[len(new_tokens)-1]
            new_tokens.append(original_tokens[i-1] + ' ' + original_tokens[i])

        elif tokens[i-1][-3:] == 'moq' and (tokens[i] in ['kerak', 'lozim', 'shart', 'darkor']):
            del new_tokens[len(new_tokens)-1]
            new_tokens.append(original_tokens[i-1] + ' ' + original_tokens[i])

        elif tokens[i-1][-3:] == 'mak' and (tokens[i] in ['kerak', 'lozim', 'shart', 'darkor']):
            del new_tokens[len(new_tokens)-1]
            new_tokens.append(original_tokens[i-1] + ' ' + original_tokens[i])

        # If none of the conditions are met, just add the current token to the new token list
        else:
            new_tokens.append(original_tokens[i])

    return new_tokens


def __change_apostrophe(text):
    # Function to swap the sign of the letters O‘o‘ and G‘g‘

    text = text.replace(f"O{chr(39)}", f"O{chr(8216)}")  # ord("'") -> ord("‘")
    text = text.replace(f"o{chr(39)}", f"o{chr(8216)}")
    text = text.replace(f"G{chr(39)}", f"G{chr(8216)}")
    text = text.replace(f"g{chr(39)}", f"g{chr(8216)}")

    text = text.replace(f"O{chr(96)}", f"O{chr(8216)}")  # ord("`") -> ord("‘")
    text = text.replace(f"o{chr(96)}", f"o{chr(8216)}")
    text = text.replace(f"G{chr(96)}", f"G{chr(8216)}")
    text = text.replace(f"g{chr(96)}", f"g{chr(8216)}")

    text = text.replace(f"O{chr(699)}", f"O{chr(8216)}")  # ord("ʻ") -> ord("‘")
    text = text.replace(f"o{chr(699)}", f"o{chr(8216)}")
    text = text.replace(f"G{chr(699)}", f"G{chr(8216)}")
    text = text.replace(f"g{chr(699)}", f"g{chr(8216)}")

    text = text.replace(f"O{chr(700)}", f"O{chr(8216)}")  # ord("ʼ") -> ord("‘")
    text = text.replace(f"o{chr(700)}", f"o{chr(8216)}")
    text = text.replace(f"G{chr(700)}", f"G{chr(8216)}")
    text = text.replace(f"g{chr(700)}", f"g{chr(8216)}")

    text = text.replace(f"O{chr(8217)}", f"O{chr(8216)}")  # ord("’") -> ord("‘")
    text = text.replace(f"o{chr(8217)}", f"o{chr(8216)}")
    text = text.replace(f"G{chr(8217)}", f"G{chr(8216)}")
    text = text.replace(f"g{chr(8217)}", f"g{chr(8216)}")

    return text


def __compound(tokens):
    # List of compound words
    compound_words = [
        # Adverb (71 units)
        [
            "bir dam", "bir kam", "bir payt", "bir qancha", "bir safar", "bir yo‘la",
            "bir yo‘lasi", "bir zamon", "bir zumda", "bu joyda", "bu kunda", "bu oyda",
            "bu vaqtda", "hali beri", "hali zamon", "har birsi", "har chorshanba", "har damda",
            "har doim", "har dushanba", "har juma", "har kechasi", "har kun", "har oqshom",
            "har payshanba", "har peshinda", "har safar", "har seshanba", "har shanba", "har soat",
            "har soniya", "har tun", "har vaqt", "har yakshanba", "har yer", "har yil",
            "har zamon", "hech bir", "hech kimsa", "hech mahal", "hech narsa", "hech vaqt",
            "hech zamon", "o‘sha daqiqada", "o‘sha joyda", "o‘sha kunda", "o‘sha oyda", "o‘sha safar",
            "o‘sha soatda", "o‘sha soniyada", "o‘sha tongda", "o‘sha tunda", "o‘sha yerda", "o‘sha zamonda",
            "shu daqiqada", "shu haftada", "shu joyda", "shu kunda", "shu oqshomda", "shu orada",
            "shu oyda", "shu payt", "shu safar", "shu soatda", "shu soniyada", "shu tongda",
            "shu vaqtda", "shu yaqinda", "shu yer", "shu zamonda", "tez orada"
        ],
        # Pronoun (26 units)
        [
            "ana o‘sha", "ana shu", "ana shular", "ana u", "bir kishi", "bir nima",
            "har bir", "har kim", "har narsa", "har nima", "har qachon", "har qanday",
            "har qaysi", "hech bir", "hech kim", "hech narsa", "hech nima", "hech qachon",
            "hech qanaqa", "hech qanday", "hech qayer", "hech qaysi", "mana bu",
            "mana bular", "mana shu", "mana shular"
        ],
        # Interjection (12 units)
        [
            "assalomu alaykum", "bor bo‘ling", "omon bo‘ling", "osh bo‘lsin",
            "salomat bo‘ling", "sog‘ bo‘ling", "vaalaykum assalom", "xush kelibsiz",
            "xush ko‘rdik", "xushvaqt bo‘ling", "xo‘p bo‘ladi", "yaxshi boring"
        ]
    ]

    # List of verb compound words (506 units)
    verb_compound_words = [
        "abadiy bo‘l", "abadiy qol", "ado et", "afsona ayla", "afsona bo‘l", "afsona qil", "ahamiyat ber",
        "ahamiyat qil", "ahd qil", "aks et", "aks qil", "amal bajar", "amal qil", "amalga osh", "amalga oshir",
        "angla yet", "aniq bo‘l", "aniq qil", "aslini olmoq", "asos sol", "avj ol", "ayon bo‘l", "azob chek",
        "azob tort", "a’zo bo‘l", "a’zo qil", "band bo‘l", "band et", "band qil", "barpo et", "bartaraf et",
        "bartaraf qil", "bas qil", "bayon ayla", "bayon et", "bayon qil", "bayram bo‘l", "bayram qil", "befarq bo‘l",
        "befarq tut", "begona bo‘l", "bir bo‘l", "birga bo‘l", "birga kel", "birga qol", "bog‘lan ol", "bog‘lan qol",
        "bog‘liq bo‘l", "bor kel", "bo‘sa ol", "buyruq ber", "buyruq qil", "chegara tort", "chiq ket", "chiqar kel",
        "chirs et", "chop et", "chop qil", "dahshat sol", "darak ber", "darak qil", "davom et", "davom qil", "dod qil",
        "dod sol", "do‘q qil", "duch bo‘l", "duch kel", "duchor ayla", "duchor bo‘l", "duchor qil", "esga ol",
        "esga sol", "e’lon qil", "e’tibor ber", "e’tibor qarat", "e’tibor qil", "faol bo‘l", "faol qil", "faraz ayla",
        "faraz et", "faraz qil", "farmon ber", "farq qil", "fikr ber", "fikr qil", "foyda ber", "foyda ol", "foyda qil",
        "g‘amxo‘r bo‘l", "g‘amxo‘rlik et", "g‘amxo‘rlik qil", "gapga qo‘y", "gapga sol", "gapga tut", "gumbur et",
        "gumon qil", "gunoh ayla", "gunoh qil", "hadik qil", "hal qil", "halok ayla", "halok bo‘l", "halok et",
        "halok qil", "haqorat et", "haqorat qil", "harakat ayla", "harakat qil", "harakatda bo‘l", "hayron bo‘l",
        "himoya qil", "himoyaga ol", "hisobga ol", "hissa qo‘sh", "hojatini chiq", "hosil ber", "hosil bo‘l",
        "hosil kir", "hosil qil", "hozir qil", "hurmat ayla", "hurmat et", "hurmat qil", "hushidan ket", "hushiga kel",
        "hushyor bo‘l", "iborat bo‘l", "ibrat bo‘l", "ichiga ol", "ichiga yut", "idrok et", "idrok qil", "ijaraga tur",
        "ijod et", "ijod qil", "ijro et", "ijro qil", "ilgari sur", "iltimos ayla", "iltimos qil", "imkon ber",
        "imkon qil", "imzo chek", "imzo qo‘y", "inkor et", "inkor qil", "inoyat ayla", "inoyat qil", "inson bo‘l",
        "inson qil", "iqror bo‘l", "ishla chiq", "ixlos qil", "jahlidan tush", "jalb et", "jalb qil", "javob ol",
        "jazavaga ayla", "jazavaga tush", "jim bo‘l", "jon kir", "joriy ayla", "joriy bo‘l", "joriy et", "joriy qil",
        "joyga tush", "kasal bo‘l", "kasal qil", "kasb et", "katta bo‘l", "katta qil", "kelib chiq", "kerak bo‘l",
        "kir bo‘l", "kir chiq", "kir qil", "ko‘r qol", "ko‘r tur", "ko‘zda tut", "ko‘ngil top", "ko‘ngil uz",
        "ko‘z yum", "ko‘zdan kechir", "kuchga kir", "kuchli bo‘l", "kuchli qil", "kun qol", "kun tush", "kuzat bor",
        "lag‘mon os", "lozim ko‘r", "madad ber", "mahrum ayla", "mahrum bo‘l", "mahrum qil", "majbur bo‘l", "majbur et",
        "majbur qil", "maqbul ko‘r", "maqbul top", "maqul top", "maydala ber", "maydala tashla", "maydala tur",
        "ma’lum qil", "ma’ruza et", "ma’ruza qil", "meros bo‘l", "meros qil", "mohir bo‘l", "mohir qil", "mos kel",
        "mushohada qil", "namoyon ayla", "namoyon et", "namoyon qil", "natija ber", "natija ol", "natija qil",
        "nazar sol", "nazarda tut", "nishonga ol", "o‘rin ber", "o‘rin egalla", "o‘rin ol", "obod ayla", "obod bo‘l",
        "obod et", "obod qil", "och ber", "ogoh ayla", "ogoh bo‘l", "ogoh et", "ogoh qil", "oh sol", "oh tort",
        "ol bor", "ol kel", "olib kel", "olib kir", "or qil", "orqaga tush", "oson bo‘l", "oson qil", "ot tashla",
        "ovora bo‘l", "ovora qil", "ovoza et", "ovoza qil", "oz bo‘l", "ozod qil", "ozor chek", "o‘pich ol",
        "o‘rnidan tur", "o‘rniga kel", "o‘sal bo‘l", "o‘sal qil", "o‘yga tol", "o‘zi kel", "pand ber", "parvarish ayla",
        "parvarish et", "parvarish qil", "parvoz et", "parvoz qil", "pastga tush", "paydo bo‘l", "paydo et",
        "paydo qil", "po‘pisa qil", "qabul ayla", "qabul et", "qabul qil", "qadr top", "qanday bo‘l", "qanday qil",
        "qaror ayla", "qaror ber", "qaror qil", "qatl et", "qatl qil", "qayd et", "qayd qil", "qayt qil", "qidir chiq",
        "qiymat ayla", "qiymat ber", "qoyil qil", "qoyil qol", "qo‘l ur", "qo‘yib yubor", "qul qil", "qulluq ayla",
        "qulluq qil", "quloq ber", "quloq os", "quloq sol", "quloq tut", "quloqqa il", "rahm ayla", "rahm qil",
        "ravo ayla", "ravo ko‘r", "ravo qil", "ravshan bo‘l", "rioya et", "rioya qil", "rizq ber", "rozi bo‘l",
        "ro‘yxat qil", "ro‘yxatdan o‘t", "ro‘yxatga ol", "ruxsat et", "ruxsat ol", "ruxsat qil", "sabab bo‘l",
        "saboq ber", "saboq chiqar", "saboq ol", "sabr ayla", "sabr et", "sabr qil", "salom ayla", "salom ayt",
        "salom ber", "samimiy bo‘l", "sarf et", "sarf qil", "sarson bo‘l", "sarson qil", "savo ber", "savol ayla",
        "savol ber", "savol tug‘", "savolga tut", "sayr ayla", "sayr qil", "shafqat ayla", "shafqat qil", "sharh qil",
        "shart qil", "shart qo‘y", "shod et", "shod qil", "shunday bo‘l", "shunday qil", "silliq qil", "sodir bo‘l",
        "sodir et", "sodir qil", "sog‘ bo‘l", "sot ol", "sovuq qot", "so‘z ber", "so‘zga sol", "sukut ayla",
        "sukut qil", "sukut saqla", "tadbiq qil", "tafovut qil", "tahrir ayla", "tahrir qil", "tahsil ol",
        "tajang bo‘l", "tajang qil", "tajriba oshir", "tajriba o‘tkaz", "taklif et", "talab et", "talab etil",
        "talab qil", "talif qil", "tamom bo‘l", "tamom qil", "tan ber", "tan ol", "tanbeh ber", "tanqid qil",
        "taqdim et", "taqdim qil", "taraq et", "tarbiya ber", "tarbiya et", "tarbiya qil", "tarixda qol", "tarjima et",
        "tarjima qil", "tark ayla", "tark qil", "tarkib top", "tartib qil", "tartibga chaqir", "tartibga sol",
        "tartibga solin", "tasdiq et", "tasdiq qil", "tashkil et", "tashkil qil", "tashkil top", "tashla ket",
        "tashrif ayla", "tashrif buyur", "tasnif qil", "tavba qil", "tavsiya et", "tavsiya qil", "taxmin ayla",
        "taxmin et", "taxmin qil", "ta’lim ber", "ta’lim qil", "ta’rif ayt", "ta’rif et", "ta’rif qil", "ta’sir ayla",
        "ta’sir et", "ta’sir ko‘r", "ta’sir qil", "ta’sis et", "ta’sis qil", "tekis qil", "telefon qil", "teng bo‘l",
        "tez qil", "tinch et", "tinch tur", "tort ol", "toza bo‘l", "toza qil", "to‘q bo‘l", "to‘y qildi", "tuhmat et",
        "tuhmat qil", "turmush qil", "turmush qur", "turmushga chiq", "turt ket", "tush ko‘r", "uf de", "uf tort",
        "uh ur", "umid et", "umid qil", "ustun tur", "uyal qol", "uyatga qol", "uzun bo‘l", "uzun et", "uzun qil",
        "vada ber", "vada et", "vada qil", "vafo ayla", "vafo et", "vafo qil", "vafot et", "va’da qil", "vertikal tush",
        "vujudga kel", "xabar ayla", "xabar ber", "xabar ol", "xabar qil", "xafa bo‘l", "xafa qil", "xarid ayla",
        "xarid qil", "xarob ayla", "xarob bo‘l", "xarob qil", "xizmat ko‘rsat", "xizmat qil", "xulosa ber",
        "xulosa chiqar", "xulosaga kel", "xursand bo‘l", "xuruj qil", "yakun top", "yangi bo‘l", "yangi qil",
        "yaqin bo‘l", "yeng o‘t", "yeng tashla", "yetarli bo‘l", "yetarli qil", "yop ber", "yordam ayla", "yordam ber",
        "yordam qil", "yordam so‘ra", "yosh to‘k", "yoz ko‘r", "yoz qoldir", "yo‘l ber", "yuz ber", "yuzaga kel",
        "zabt et", "zabt qil", "zamin yarat", "zarar ber", "zarar et", "zarar kel", "zarar qil", "ziyon kel",
        "ziyon qil"
    ]

    # Flatten the compound_words list for easier checking
    all_compound_words = []
    for category in compound_words:
        all_compound_words.extend(category)

    # Initialize an empty list to store the new tokens
    new_tokens = []
    i = 0
    while i < len(tokens):
        # Check for compound words with 2 tokens
        if i + 1 < len(tokens):
            two_word = tokens[i] + ' ' + tokens[i + 1]
            if __change_apostrophe(two_word).lower() in [word for word in all_compound_words]:
                new_tokens.append(two_word)
                i += 2
                continue

        # Check for verb compound words (with affixes)
        if i + 1 < len(tokens):
            # Check if the current token and the next token form a verb compound
            for lemma in verb_compound_words:
                if __change_apostrophe(tokens[i]).lower().startswith(lemma.split()[0]) and \
                        __change_apostrophe(tokens[i + 1]).lower().startswith(lemma.split()[1]):
                    new_tokens.append(tokens[i] + ' ' + tokens[i + 1])
                    i += 2
                    break
            else:
                # If no compound word is found, add the current token as is
                new_tokens.append(tokens[i])
                i += 1
        else:
            # If no compound word is found, add the current token as is
            new_tokens.append(tokens[i])
            i += 1

    return new_tokens


def __kfsq(tokens):  # noqa

    # Total 1235 units
    kfsq = [  # Uzbek: Ko‘makchi fe'lli so‘z qo‘shilmasi
        "alahsira chiq", "angla tur", "angla yet", "art bo‘l", "art boshla", "art chiq", "art ol", "ayir chiq",
        "ayir ol", "aylan chiq", "aylan kel", "aylan yur", "ayt qol", "ayt tashla", "ayt tur", "ayt ber", "ayt yubor",
        "baqir chiq", "baqir tashla", "belgila chiq", "belgila ol", "belgila qo‘y", "belgila tashla", "ber tur",
        "bil yur", "bo‘l o‘t", "bo‘l qol", "bo‘l tashla", "bo‘zray tur", "boq tur", "boq yur", "bor tur", "bor yur",
        "bor kel", "buzil ket", "chaqir kel", "charcha boshla", "chay boshla", "chay ol", "chay qo‘y", "chay tashla",
        "chiq ket", "chiq qol", "chiz tur", "cho‘chi ket", "cho‘zil ket", "dikkay qol", "dikkay tur", "dodla boshla",
        "dodla chiq", "durilla ket", "eskir ket", "eskir qol", "foydalan kel", "gapir boshla", "gapir chiq",
        "gapir ket", "gapir qo‘y", "gapir tashla", "hilpira boshla", "hilpirab tur", "hisobla chiq", "hisobla tashla",
        "hurk boshla", "hurk ket", "hurk qol", "hurpay ket", "hurpay tur", "ich tashla", "il qo‘y", "ishla qol",
        "ishla tashla", "ishla tur", "ishla yot", "ishla yur", "jo‘na boshla", "jo‘na ket", "jo‘na qol", "jo‘nat ber",
        "jo‘nat tashla", "jo‘nat tur", "jo‘nat yubor", "kech chiq", "kech o‘t", "kechik kel", "kechik qol",
        "keksay qol", "kel qol", "kel tur", "kel yur", "keltir tashla", "keltir tur", "keng boshla", "keng ket",
        "keng qol", "kengay ket", "kirit ol", "kirit qol", "kiy ol", "kiy yur", "ko‘ch ket", "ko‘chir ol",
        "ko‘chir tashla", "ko‘kar ket", "ko‘kar qol", "ko‘pay ket", "ko‘paytir tur", "ko‘r chiq", "ko‘r ol", "ko‘r qol",
        "ko‘r tashla", "ko‘r tur", "ko‘r chiq", "ko‘rsat qo‘y", "ko‘rsat tashla", "ko‘rsat tur", "ko‘tar ol",
        "ko‘taril tur", "kuchaytir ber", "kuchaytir qo‘y", "kul boshla", "kul chiq", "kul ol", "kul tur", "kul yot",
        "kula boshla", "kut boshla", "kut ol", "kut tur", "kut yur", "kuyla ber", "kuyla bo‘l", "kuyla boshla",
        "kuyla ket", "kuzat qol", "maqta boshla", "maqta tashla", "o‘l tashla", "o‘qi chiq", "o‘qi ol", "o‘qi tashla",
        "o‘qi tur", "o‘qi yur", "o‘tir chiq", "o‘tir qol", "o‘yla chiq", "o‘yla ket", "o‘yla ko‘r", "o‘yla tur",
        "o‘yla yur", "o‘ylab tur", "o‘ylab yur", "o‘ylan qol", "o‘ylan qol", "o‘zgar ket", "o‘zgar qol",
        "o‘zlashtir ol", "och qo‘y", "och tashla", "ol kel", "oq ket", "oqsa tur", "oqsa yur", "osh bor", "osh ket",
        "otil chiq", "ozay ket", "ozay qol", "pasay ket", "pasay qol", "qama qo‘y", "qama tashla", "qara tur",
        "qarash yur", "qaytar ber", "qazi boshla", "qazi tashla", "qil qo‘y", "qil tashla", "qil ber", "qir tashla",
        "qir yur", "qirq tashla", "qisqart qo‘y", "qiyna tashla", "qizar ket", "qizar qol", "qo‘rq ket", "qo‘rq tur",
        "qo‘rq yur", "qo‘sh ayt", "qo‘sh tashla", "qo‘sh yubor", "qopla ol", "qoq kel", "qot qol", "ranjit qo‘y",
        "sakra yur", "sana boshla", "sana chiq", "sana keta", "saqla tur", "saqla yur", "sarg‘ay ket", "sarg‘ay qol",
        "sayra chiq", "sev boshla", "shalpay qol", "shil tashla", "shosh qol", "so‘k tashla", "so‘ra tur", "so‘ra yur",
        "so‘zla tashla", "sog‘ay boshla", "sog‘ay ket", "sog‘ay ol", "sot tashla", "supur tashla", "supur tur",
        "supur yur", "sur qo‘y", "sur tashla", "susay qol", "suvsira qol", "suyul ket", "ta’minla ber", "ta’minla ol",
        "ta’minla tur", "tarqat ber", "tarqat tur", "tarqat yur", "tebrat tur", "tebrat yur", "tekshir boshla",
        "tekshir chiq", "tekshir ol", "tekshir qol", "termul tur", "tezlat qo‘y", "tinch qol", "titrat tur",
        "to‘k tashla", "to‘la tur", "to‘la yur", "to‘ldir bo‘l", "to‘ldir tashla", "to‘zg‘it tashla", "top ber",
        "tort tashla", "tortish boshla", "turtil ket", "tush boshla", "tush qol", "tushun ol", "tushir ber",
        "tushir yubor", "tushun tur", "tut qol", "tuzla boshla", "tuzla chiq", "tuzla qo‘y", "tuzla tashla", "uch yur",
        "uchrash boshla", "uchrash kel", "uchrash qol", "uchrash tur", "uchrash yur", "ulg‘ay ket", "ur tashla",
        "ur tur", "urish boshla", "urish ket", "urish tur", "urish yur", "ushla boshla", "ushla ol", "ushla qol",
        "ushla tur", "uxla qol", "uyqisira chiq", "yarat bo‘l", "yarat chiq", "yarat ol", "yarat tashla", "yarqira ket",
        "yasha boshla", "yashir tashla", "yashirin tur", "yashirin yur", "ye tashla", "ye tur", "ye qo‘y", "yech ol",
        "yech qo‘y", "yech tashla", "yetkaz ber", "yig‘ boshla", "yig‘la ket", "yiqil ket", "yiqil yoz", "yodla boshla",
        "yodla chiq", "yodla tashla", "yomonla tashla", "yoq qol", "yoq tashla", "yoq tush", "yorit tur", "yorit yur",
        "yot qol", "yoz ber", "yoz chiq", "yoz o‘tir", "yoz ol", "yoz tashla", "yoz tur", "yoz yur", "yoz boshla",
        "yoz tashla", "yugur tur", "yur boshla", "yur ket", "yura boshla", "yura ketti", "yuv tashla", "yuvin tur",
        "yuvintir qo‘y", "achin boshla", "achin ol", "achin qo‘y", "ajrat ko‘rsat", "art qo‘y", "art tashla",
        "art yubor", "art yur", "ayt ber", "bil boshla", "bil ol", "bil qol", "bo‘g‘a ol", "bo‘l ol", "bo‘shash boshla",
        "bo‘shash ol", "bo‘shash qol", "bog‘a boshla", "bog‘la qo‘y", "bos boshla", "bos ol", "bos qol", "bos tashla",
        "bukilib-bukil ket", "charcha bo‘l", "charcha qol", "duch kel", "ich chiq", "ich ol", "ich qo‘y", "ich to‘xta",
        "ich yubor", "i̇shlab chiqar", "kel boshla", "kelish ol", "kelish qo‘y", "kelish yubor", "kelish yur", "kes ol",
        "kes o‘t", "ket boshla", "ket qol", "ko‘tar qo‘y", "kut yur", "kuy boshla", "kuydir ol", "kuydir qo‘y",
        "o‘r tur", "o‘tkaz ko‘r", "og‘ri boshla", "og‘ri qol", "ol chiq", "ol sot", "ot boshla", "ot ol", "ot yubor",
        "otil chiq", "pishir ol", "pishir qo‘y", "qaytar boshla", "qaytar chiq", "qaytar ol", "qaytar qo‘y",
        "qaytar yubor", "qaytar yur", "qo‘y yubor", "qotir boshla", "qotir qo‘y", "quvon boshla", "quvon ket",
        "quyil boshla", "rivojlan bor", "saqla chiq", "saqla ol", "saqla qol", "saqla yubor", "savala boshla",
        "savala ol", "savala qo‘y", "savala tashla", "shakllan bor", "shalvira qol", "shalvira tur", "shalvira tush",
        "shamolla bo‘l", "shamolla boshla", "shamolla qol", "silkit boshla", "silkit ol", "silkit qo‘y", "sirg‘al ket",
        "sirg‘al tush", "so‘zla boshla", "so‘zla o‘tir", "so‘zla yubor", "so‘zla yur", "suz ket", "tasdiqni kir",
        "tashla ko‘r", "tashla yubor", "teg tur", "tekisla qo‘y", "tekisla yur", "ter ber", "ter bo‘l", "ter boshla",
        "ter chiq", "ter ol", "ter qo‘y", "ter tashla", "ter tur", "tinch tur", "to‘xta ol", "to‘xta qol",
        "to‘xtat qo‘y", "to‘xtat yubor", "tug qol", "tuga qol", "tur ol", "tur qol", "tutoqi ket", "tutoqi qol",
        "uqi ol", "uqi qol", "ur o‘t", "ur qol", "urini ko‘r", "uz ol", "uzoqlash bor", "yarat bil", "yarat yubor",
        "yarat yur", "yasha o‘t", "yasha qol", "yasha tur", "yet bor", "yet boshla", "yet qol", "yopiril kel",
        "yopiril boshla", "yopiril ket", "yopiril ol", "yopish boshla", "yopish ol", "yopish qol", "yorish ket",
        "yorish ko‘rin", "yoz qol", "yukla ol", "zerik ket", "zerik qol", "ajral chiq" "alangalash chiq",
        "alangalash ket", "alangalash qol", "aloqa qil", "amal qil", "amal boshla", "amal top", "angla chiq",
        "angla qol", "angla yur", "aniqla chiq", "aniqla ol", "aniqla tur", "aniqla yur", "aniq qol", "aniq tur",
        "aralash chiq", "aralash ket", "aralash qol", "aralash tur", "aralash yur", "aylan boshla", "aylan tur",
        "aylan yur", "aylan ol", "aylan qo‘y", "aylan tashla", "ayril boshla", "ayril chiq", "ayril qol", "ayril tur",
        "ayril yur", "ayt boshla", "ayt tur", "ayt yur", "ayt ol", "ayt qo‘y", "ayt tashla", "ayt ket", "ayt chiq",
        "ayt ko‘r", "ayt yubor", "aytil tur", "aytil yur", "bahs qil", "bahslash chiq", "bahslash ket", "bahslash qol",
        "bahslash tur", "bahslash yur", "baxtiyor bo‘l", "baxtiyor qil", "belgilab chiq", "belgilab qo‘y",
        "belgilab tashla", "ber boshla", "ber chiq", "ber ol", "ber qol", "ber tur", "ber yur", "ber ko‘r",
        "ber tashla", "ber yubor", "bilan yur", "bil boshla", "bil tur", "bil yur", "bil chiq", "bil ol", "bil qo‘y",
        "bil tashla", "bil ket", "bilmadim qol", "bilmadim tur", "bilmadim yur", "birlashtir chiq", "birlashtir ol",
        "birlashtir tashla", "birlik bo‘l", "bo‘l boshla", "bo‘l tur", "bo‘l yur", "bo‘l chiq", "bo‘l qo‘y",
        "bo‘l tashla", "bo‘l ket", "bo‘lib ket", "bo‘lib qol", "borib kel", "borib qol", "borib tur", "borib yur",
        "borib chiq", "borib ol", "borib tashla", "borib qo‘y", "borib yubor", "boq boshla", "boq tur", "boq yur",
        "boq chiq", "boq ol", "boq qo‘y", "boq tashla", "boq yubor", "bos boshla", "bos tur", "bos yur", "bos chiq",
        "bos ol", "bos qol", "bos tashla", "bos qo‘y", "bos yubor", "bosib ket", "bosib qol", "bosib tur", "bosib yur",
        "bosib chiq", "bosib ol", "bosib tashla", "bosib qo‘y", "bosib yubor", "bukil boshla", "bukil tur", "bukil yur",
        "bukil chiq", "bukil ol", "bukil qol", "bukil tashla", "bukil qo‘y", "bukil yubor", "buz boshla", "buz tur",
        "buz yur", "buz chiq", "buz ol", "buz qol", "buz tashla", "buz qo‘y", "buz yubor", "charchab qol",
        "charchab tur", "charchab yur", "charchab chiq", "charchab ol", "charchab tashla", "charchab qo‘y",
        "charchab yubor", "chiq boshla", "chiq tur", "chiq yur", "chiq ol", "chiq qol", "chiq tashla", "chiq qo‘y",
        "chiq yubor", "chiqib ket", "chiqib qol", "chiqib tur", "chiqib yur", "chiqib chiq", "chiqib ol",
        "chiqib tashla", "chiqib qo‘y", "chiqib yubor", "chop boshla", "chop tur", "chop yur", "chop chiq", "chop ol",
        "chop qol", "chop tashla", "chop qo‘y", "chop yubor", "chopib ket", "chopib qol", "chopib tur", "chopib yur",
        "chopib chiq", "chopib ol", "chopib tashla", "chopib qo‘y", "chopib yubor", "chuqur bo‘l", "chuqur qil",
        "chuqurlash boshla", "chuqurlash tur", "chuqurlash yur", "chuqurlash chiq", "chuqurlash ol", "chuqurlash qol",
        "chuqurlash tashla", "chuqurlash qo‘y", "chuqurlash yubor", "davom bo‘l", "davom et", "davom qil",
        "davom boshla", "davom tur", "davom yur", "davom chiq", "davom ol", "davom qol", "davom tashla", "davom qo‘y",
        "davom yubor", "deb ayt", "deb qo‘y", "deb tashla", "deb yubor", "deb tur", "deb yur", "deb chiq", "deb ol",
        "deb qol", "deyarli bo‘l", "deyarli qil", "diqqat qil", "diqqat bo‘l", "diqqat boshla", "diqqat tur",
        "diqqat yur", "diqqat chiq", "diqqat ol", "diqqat qol", "diqqat tashla", "diqqat qo‘y", "diqqat yubor",
        "doim bo‘l", "doim qil", "doimiy bo‘l", "doimiy qil", "doimiylash boshla", "doimiylash tur", "doimiylash yur",
        "doimiylash chiq", "doimiylash ol", "doimiylash qol", "doimiylash tashla", "doimiylash qo‘y",
        "doimiylash yubor", "domla bo‘l", "domla qil", "domla boshla", "domla tur", "domla yur", "domla chiq",
        "domla ol", "domla qol", "domla tashla", "domla qo‘y", "domla yubor", "dunyo bo‘l", "dunyo qil", "dunyo boshla",
        "dunyo tur", "dunyo yur", "dunyo chiq", "dunyo ol", "dunyo qol", "dunyo tashla", "dunyo qo‘y", "dunyo yubor",
        "dunyoda bo‘l", "dunyoda qil", "dunyoda boshla", "dunyoda tur", "dunyoda yur", "dunyoda chiq", "dunyoda ol",
        "dunyoda qol", "dunyoda tashla", "dunyoda qo‘y", "dunyoda yubor" "erish boshla", "erish tur", "erish yur",
        "erish chiq", "erish ol", "erish qol", "erish tashla", "erish qo‘y", "erish yubor", "esga ol", "esga sol",
        "eslab qol", "eslab tur", "eslab yur", "eslab chiq", "eslab ol", "eslab tashla", "eslab qo‘y", "eslab yubor",
        "eshit boshla", "eshit tur", "eshit yur", "eshit chiq", "eshit ol", "eshit qol", "eshit tashla", "eshit qo‘y",
        "eshit yubor", "farq qil", "farq boshla", "farq tur", "farq yur", "farq chiq", "farq ol", "farq qol",
        "farq tashla", "farq qo‘y", "farq yubor", "fikr qil", "fikr boshla", "fikr tur", "fikr yur", "fikr chiq",
        "fikr ol", "fikr qol", "fikr tashla", "fikr qo‘y", "fikr yubor", "foyda ol", "foyda qil", "foyda boshla",
        "foyda tur", "foyda yur", "foyda chiq", "foyda ol", "foyda qol", "foyda tashla", "foyda qo‘y", "foyda yubor",
        "gapir boshla", "gapir tur", "gapir yur", "gapir chiq", "gapir ol", "gapir qol", "gapir tashla", "gapir qo‘y",
        "gapir yubor", "g‘amxo‘r bo‘l", "g‘amxo‘r qil", "g‘amxo‘r boshla", "g‘amxo‘r tur", "g‘amxo‘r yur",
        "g‘amxo‘r chiq", "g‘amxo‘r ol", "g‘amxo‘r qol", "g‘amxo‘r tashla", "g‘amxo‘r qo‘y", "g‘amxo‘r yubor",
        "g‘azab qil", "g‘azab boshla", "g‘azab tur", "g‘azab yur", "g‘azab chiq", "g‘azab ol", "g‘azab qol",
        "g‘azab tashla", "g‘azab qo‘y", "g‘azab yubor", "gumon qil", "gumon boshla", "gumon tur", "gumon yur",
        "gumon chiq", "gumon ol", "gumon qol", "gumon tashla", "gumon qo‘y", "gumon yubor", "gunoh qil", "gunoh boshla",
        "gunoh tur", "gunoh yur", "gunoh chiq", "gunoh ol", "gunoh qol", "gunoh tashla", "gunoh qo‘y", "gunoh yubor",
        "hal qil", "hal boshla", "hal tur", "hal yur", "hal chiq", "hal ol", "hal qol", "hal tashla", "hal qo‘y",
        "hal yubor", "hayron qol", "hayron tur", "hayron yur", "hayron chiq", "hayron ol", "hayron tashla",
        "hayron qo‘y", "hayron yubor", "hisobla chiq", "hisobla ol", "hisobla qol", "hisobla qo‘y", "hisobla yubor",
        "hisob qil", "hisob boshla", "hisob tur", "hisob yur", "hisob chiq", "hisob ol", "hisob tashla", "hisob qo‘y",
        "hisob yubor", "hissa qo‘sh", "hissa ol", "hissa ber", "hozir bo‘l", "hozir qil", "hozir boshla", "hozir tur",
        "hozir yur", "hozir chiq", "hozir ol", "hozir qol", "hozir tashla", "hozir qo‘y", "hozir yubor", "hurmat qil",
        "hurmat boshla", "hurmat tur", "hurmat yur", "hurmat chiq", "hurmat ol", "hurmat qol", "hurmat tashla",
        "hurmat qo‘y", "hurmat yubor", "hushyor bo‘l", "hushyor qil", "hushyor boshla", "hushyor tur", "hushyor yur",
        "hushyor chiq", "hushyor ol", "hushyor qol", "hushyor tashla", "hushyor qo‘y", "hushyor yubor", "iborat bo‘l",
        "iborat qil", "iborat boshla", "iborat tur", "iborat yur", "iborat chiq", "iborat ol", "iborat qol",
        "iborat tashla", "iborat qo‘y", "iborat yubor", "idrok qil", "idrok boshla", "idrok tur", "idrok yur",
        "idrok chiq", "idrok ol", "idrok qol", "idrok tashla", "idrok qo‘y", "idrok yubor", "ijod qil", "ijod boshla",
        "ijod tur", "ijod yur", "ijod chiq", "ijod ol", "ijod qol", "ijod tashla", "ijod qo‘y", "ijod yubor",
        "ijro qil", "ijro boshla", "ijro tur", "ijro yur", "ijro chiq", "ijro ol", "ijro qol", "ijro tashla",
        "ijro qo‘y", "ijro yubor", "iltimos qil", "iltimos boshla", "iltimos tur", "iltimos yur", "iltimos chiq",
        "iltimos ol", "iltimos qol", "iltimos tashla", "iltimos qo‘y", "iltimos yubor", "imkon qil", "imkon boshla",
        "imkon tur", "imkon yur", "imkon chiq", "imkon ol", "imkon qol", "imkon tashla", "imkon qo‘y", "imkon yubor",
        "imzo chek", "imzo qo‘y", "imzo ol", "imzo ber", "imzo tashla", "imzo yubor", "inson qil", "inson bo‘l",
        "inson boshla", "inson tur", "inson yur", "inson chiq", "inson ol", "inson qol", "inson tashla", "inson qo‘y",
        "inson yubor", "iqror bo‘l", "iqror qil", "iqror boshla", "iqror tur", "iqror yur", "iqror chiq", "iqror ol",
        "iqror qol", "iqror tashla", "iqror qo‘y", "iqror yubor", "ishla boshla", "ishla chiq", "ishla qol",
        "ishla tur", "ishla yur", "ishla ol", "ishla tashla", "ishla qo‘y", "ishla yubor" "jalb qil", "jalb boshla",
        "jalb tur", "jalb yur", "jalb chiq", "jalb ol", "jalb qol", "jalb tashla", "jalb qo‘y", "jalb yubor",
        "javob ber", "javob ol", "javob qil", "javob boshla", "javob tur", "javob yur", "javob chiq", "javob qol",
        "javob tashla", "javob qo‘y", "javob yubor", "jim qol", "jim tur", "jim yur", "jim chiq", "jim ol",
        "jim tashla", "jim qo‘y", "jim yubor", "joriy qil", "joriy bo‘l", "joriy boshla", "joriy tur", "joriy yur",
        "joriy chiq", "joriy ol", "joriy qol", "joriy tashla", "joriy qo‘y", "joriy yubor", "kasal bo‘l", "kasal qil",
        "kasal boshla", "kasal tur", "kasal yur", "kasal chiq", "kasal ol", "kasal qol", "kasal tashla", "kasal qo‘y",
        "kasal yubor", "katta bo‘l", "katta qil", "katta boshla", "katta tur", "katta yur", "katta chiq", "katta ol",
        "katta qol", "katta tashla", "katta qo‘y", "katta yubor", "kel boshla", "kel tur", "kel yur", "kel chiq",
        "kel ol", "kel qol", "kel tashla", "kel qo‘y", "kel yubor", "kerak bo‘l", "kerak qil", "kerak boshla",
        "kerak tur", "kerak yur", "kerak chiq", "kerak ol", "kerak qol", "kerak tashla", "kerak qo‘y", "kerak yubor",
        "ko‘r boshla", "ko‘r tur", "ko‘r yur", "ko‘r chiq", "ko‘r ol", "ko‘r qol", "ko‘r tashla", "ko‘r qo‘y",
        "ko‘r yubor", "ko‘ngil top", "ko‘ngil uz", "ko‘ngil bo‘l", "ko‘ngil qil", "ko‘ngil boshla", "ko‘ngil tur",
        "ko‘ngil yur", "ko‘ngil chiq", "ko‘ngil ol", "ko‘ngil qol", "ko‘ngil tashla", "ko‘ngil qo‘y", "ko‘ngil yubor",
        "ko‘zda tut", "ko‘z yum", "ko‘z boshla", "ko‘z tur", "ko‘z yur", "ko‘z chiq", "ko‘z ol", "ko‘z qol",
        "ko‘z tashla", "ko‘z qo‘y", "ko‘z yubor", "ko‘zdan kechir", "ko‘zdan o‘t", "ko‘zdan chiq", "ko‘zdan qol",
        "kuchli bo‘l", "kuchli qil", "kuchli boshla", "kuchli tur", "kuchli yur", "kuchli chiq", "kuchli ol",
        "kuchli qol", "kuchli tashla", "kuchli qo‘y", "kuchli yubor", "kun tush", "kun qol", "kun bo‘l", "kun qil",
        "kun boshla", "kun tur", "kun yur", "kun chiq", "kun ol", "kun tashla", "kun qo‘y", "kun yubor", "lag‘mon os",
        "lag‘mon qo‘y", "lag‘mon ol", "lag‘mon tashla", "lag‘mon yubor", "lozim ko‘r", "lozim bo‘l", "lozim qil",
        "lozim boshla", "lozim tur", "lozim yur", "lozim chiq", "lozim ol", "lozim qol", "lozim tashla", "lozim qo‘y",
        "lozim yubor", "madad ber", "madad ol", "madad qil", "madad boshla", "madad tur", "madad yur", "madad chiq",
        "madad qol", "madad tashla", "madad qo‘y", "madad yubor", "mahrum bo‘l", "mahrum qil", "mahrum boshla",
        "mahrum tur", "mahrum yur", "mahrum chiq", "mahrum ol", "mahrum qol", "mahrum tashla", "mahrum qo‘y",
        "mahrum yubor", "majbur bo‘l", "majbur qil", "majbur boshla", "majbur tur", "majbur yur", "majbur chiq",
        "majbur ol", "majbur qol", "majbur tashla", "majbur qo‘y", "majbur yubor", "maqbul ko‘r", "maqbul bo‘l",
        "maqbul qil", "maqbul boshla", "maqbul tur", "maqbul yur", "maqbul chiq", "maqbul ol", "maqbul qol",
        "maqbul tashla", "maqbul qo‘y", "maqbul yubor", "ma’lum bo‘l", "ma’lum qil", "ma’lum boshla", "ma’lum tur",
        "ma’lum yur", "ma’lum chiq", "ma’lum ol", "ma’lum qol", "ma’lum tashla", "ma’lum qo‘y", "ma’lum yubor",
        "meros bo‘l", "meros qil", "meros boshla", "meros tur", "meros yur", "meros chiq", "meros ol", "meros qol",
        "meros tashla", "meros qo‘y", "meros yubor", "mohir bo‘l", "mohir qil", "mohir boshla", "mohir tur",
        "mohir yur", "mohir chiq", "mohir ol", "mohir qol", "mohir tashla", "mohir qo‘y", "mohir yubor", "mos kel",
        "mos bo‘l", "mos qil", "mos boshla", "mos tur", "mos yur", "mos chiq", "mos ol", "mos qol", "mos tashla",
        "mos qo‘y", "mos yubor", "mushohada qil", "mushohada boshla", "mushohada tur", "mushohada yur",
        "mushohada chiq", "mushohada ol", "mushohada qol", "mushohada tashla", "mushohada qo‘y",
        "mushohada yubor" "namoyon bo‘l", "namoyon qil", "namoyon boshla", "namoyon tur", "namoyon yur", "namoyon chiq",
        "namoyon ol", "namoyon qol", "namoyon tashla", "namoyon qo‘y", "namoyon yubor", "natija ber", "natija ol",
        "natija qil", "natija boshla", "natija tur", "natija yur", "natija chiq", "natija qol", "natija tashla",
        "natija qo‘y", "natija yubor", "nazar sol", "nazar qil", "nazar boshla", "nazar tur", "nazar yur", "nazar chiq",
        "nazar ol", "nazar qol", "nazar tashla", "nazar qo‘y", "nazar yubor", "nishonga ol", "nishonga qo‘y",
        "nishonga tashla", "nishonga yubor"
    ]

    new_tokens = []
    i = 0
    while i < len(tokens):
        if i + 1 < len(tokens):
            # Check if the current token and the next token form a kfsq
            for f in kfsq:
                if __change_apostrophe(tokens[i]).lower().startswith(f.split()[0]) and \
                        __change_apostrophe(tokens[i + 1]).lower().startswith(f.split()[1]):
                    new_tokens.append(tokens[i] + ' ' + tokens[i + 1])
                    i += 2
                    break
            else:
                # If no kfsq is found, add the current token as is
                new_tokens.append(tokens[i])
                i += 1
        else:
            # If no kfsq is found, add the current token as is
            new_tokens.append(tokens[i])
            i += 1

    return new_tokens


def tokenize(text, punctuation=True):
    # Split the input text into individual tokens by whitespace
    tokens = text.split()

    # Process the tokens for division (like: ["(yangilik)"] to ["(", "yangilik", ")"])
    tokens = __division(tokens)

    # Process the tokens for gerunds (like: "-(u)v, -(i)sh, -moq, -mak" + "kerak, lozim, shart, darkor")
    tokens = __gerund(tokens)

    # Process the tokens for compound words (e.g., handling hyphenated words like 'high-end')
    tokens = __compound(tokens)

    # Process the tokens for keyword and special query handling (likely related to search optimization)
    tokens = __kfsq(tokens)

    # If the punctuation flag is set to True, return the tokens including punctuation
    if punctuation:
        return tokens
    else:
        # If punctuation flag is False, filter out punctuation tokens
        no_punc_tokens = []

        # Loop through each token and include only alphanumeric tokens (words)
        for token in tokens:
            if re.match(r'\w+', token):  # It's a word (alphanumeric)
                no_punc_tokens.append(token)

        return no_punc_tokens
