import logging
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import quote, urlparse

import feedparser
import requests
from models.article import Article
from core.extraction import decode_google_url

logger = logging.getLogger(__name__)


def create_search_url(user_query: str):
    normalized = re.sub(r"\s+", " ", user_query).strip()
    
    rss_url = f"https://news.google.com/rss/search?q={quote(normalized)}+when:1d"
    logger.info(f"RSS url:\t{rss_url}")
    return rss_url


def get_articles_from_rss(query: str, limit: int | None = None) -> list[Article]:
    """Get articles from Google RSS for the given search query within the past 24 hours."""
    rss_url = create_search_url(query)
    response = requests.get(rss_url, timeout=10)
    response.raise_for_status()
    feed = feedparser.parse(response.content)

    logger.info(f"Feed status: {feed.get('status')}")
    logger.debug(f"Feed: {feed}")
    logger.info(f"Found {len(feed.entries)} articles")

    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    top_urls = ["reuters.com", "apnews.com", "aninews.in", "afp.com", "bloomberg.com", "xinhuanet.com", "cgtn.com", "globaltimes.cn", 
                "tass.com", "sputniknews.com", "rt.com", "nytimes.com", "washingtonpost.com", "cnn.com", "foxnews.com", "bbc.com", "staradvertiser.com", 
                "hawaiinewsnow.com", "kitv.com", "hawaiitribune-herald.com", "thegardenisland.com", "mauinews.com", "westhawaiitoday.com", "civilbeat.org", 
                "bizjournals.com", "military.com", "defensenews.com", "breakingdefense.com", "stripes.com", "twz.com", "taskandpurpose.com", "navytimes.com", 
                "armytimes.com", "airforcetimes.com", "defenseone.com", "warontherocks.com", "janes.com", "foreignpolicy.com", "nationalinterest.org", 
                "defensescoop.com", "c4isrnet.com", "wsj.com", "businessinsider.com", "cbsnews.com/60-minutes", "kuenselonline.com", "bbs.bt", "thebhutanese.bt", 
                "bhutantimes.bt", "bhutanobserver.bt", "bhutantoday.bt", "businessbhutan.bt", "drukyoedzer.bt", "gnhc.gov.bt", "nauru.gov.nr", "naurugov.nr", 
                "centralstarnews.com", "mwinenko.com", "nauruchronicle.com", "nmb.gov.nr", "radionauru.nr", "pireport.org", "rnz.co.nz", "olo.news", 
                "talaomatagi.com", "tuvalunewsheet.tv", "tuvaluechoes.com", "fenui.news", "sikuleo.tv", "president.gov.tv", "tmc.tv", "tuvalu.tv", 
                "tuvaluonline.tv", "marshallislandsjournal.com", "yokwe.net", "rmiembassyus.org", "v7ab.com", "mbc.fm", "myafn.net", "islandtimes.us", 
                "kilikili.net", "pressport.com", "kiribatiupdates.com", "kiribatinews.com", "radio.gov.ki", "mic.gov.ki", "islandreporter.com", 
                "president.gov.ki", "niuestar.co.nz", "gov.nu", "abc.net.au", "niue.nu", "tiabelau.com", "palaugov.pw", "islandscene.org", "pwnews.com", 
                "palau.net", "cookislandsnews.com", "cookislands.gov.ck", "loopnews.com", "ryukyushimpo.jp", "okinawatimes.co.jp", "nhk.or.jp", "rbc.co.jp", 
                "otv.co.jp", "qab.co.jp", "fmokinawa.co.jp", "okinawa-report.com", "okinawastandard.com", "tntv.pf", "kpress.info", "fsmpublicinfo.gov.fm", 
                "pohnpeitribune.com", "yapnetwork.com", "chuuktribune.com", "kosrae.gov.fm", "fm103.fm", "onlinekhabar.com", "ekantipur.com", "kathmandupost.com", 
                "thehimalayantimes.com", "annapurnapost.com", "nepalitimes.com", "nagariknetwork.com", "setopati.com", "ratopati.com", "gorkhapatraonline.com", 
                "risingnepaldaily.com", "dw.com", "sajha.com.np", "english.kantipur.com", "imagechannel.com.np", "madhespost.com", "ladepeche.pf", "tahiti-infos.com", 
                "fenuanews.com", "tahititoday.pf", "la1ere.francetvinfo.fr", "tahiti-numerique.pf", "radio1.pf", "tahitipacifique.com", "presidence.pf", "lnc.nc", 
                "demain.nc", "geckonews.nc", "lechienbleu.nc", "caledonia.news", "ncstop.com", "nctv.nc", "djiido.com", "kanaknews.com", "matangitonga.to", 
                "tonga-broadcasting.net", "timesoftonga.com", "kalea.to", "taimiotonga.com", "tongachronicle.to", "radiotonga.to", "televisiontonga.to", 
                "tongadailynews.to", "gov.to", "stuff.co.nz", "nzherald.co.nz", "tvnz.co.nz", "newshub.co.nz", "1news.co.nz", "scoop.co.nz", "thespinoff.co.nz", 
                "odt.co.nz", "press.co.nz", "nbr.co.nz", "newsroom.co.nz", "newstalkzb.co.nz", "theconversation.com", "metromag.co.nz", "fijitimes.com", 
                "fijisun.com.fj", "fbctv.com.fj", "fijivillage.com", "loopfiji.com", "fijilive.com", "pina.com.fj", "islandsbusiness.com", "radiofiji.com.fj", 
                "mailife.com.fj", "thejetnewspaper.com", "fijione.tv", "nadroga.com", "solomonstarnews.com", "solomontimes.com", "islandsun.com.sb", 
                "sibconline.com.sb", "wantok.com.sb", "postcourier.com.pg", "solomonislandsherald.com", "solomonvoice.com", "dailypost.vu", "vanuatuindependent.com", 
                "loopvanuatu.com", "radiovanuatu.gov.vu", "vbtc.vu", "vanuatuweekly.com", "vanuatudailynews.com", "lhebdo.vu", "vanuatu.travel", "tatoli.tl", 
                "timorpost.com", "suaratimorlorosae.com", "independente.tl", "diliweekly.com", "dailynacional.tl", "rttljp.com", "tnews.tl", "miadhu.com", 
                "verdadefeeling.com", "lusa.pt", "thenational.com.pg", "looppng.com", "emtv.com.pg", "pngtoday.com", "pacnews.com", "wantok.com.pg", 
                "pngpost.com", "irrawaddy.com", "myanmar-now.org", "mizzima.com", "dvb.no", "mmtimes.com", "frontiermyanmar.net", "elevenmyanmar.com", 
                "7day.news", "gnlm.com.mm", "khitthitmedia.com", "rfa.org", "voanews.com", "coconuts.co", "thevoicejournal.com", "moi.gov.mm", 
                "bnionline.net", "myanmardigitalnews.com", "moemaka.com", "thediplomat.com", "udn.com", "ettoday.net", "ltn.com.tw", "chinatimes.com", 
                "tvbs.com.tw", "nextapple.com", "taipeitimes.com", "cna.com.tw", "cts.com.tw", "setn.com", "ftvnews.com.tw", "taiwannews.com.tw", "storm.mg", 
                "mirrormedia.mg", "twreporter.org", "cw.com.tw", "bnext.com.tw", "want-daily.com", "yahoo.com", "vientianetimes.org", "vientianemai.net", 
                "pasaxon.org.la", "kpl.gov.la", "laotiantimes.com", "lntv.gov.la", "phattananews.com", "kohsantepheapdaily.com.kh", "freshnewsasia.com", 
                "sabay.com.kh", "vodenglish.news", "phnompenhpost.com", "cambodiadaily.com", "khmertimeskh.com", "rasmeinews.com", "cambodianess.com", 
                "tvk.gov.kh", "bayontv.com.kh", "camboja.com.kh", "voacambodia.com", "postkhmer.com", "mirmirror.com.kh", "khmerload.com", "thmeythmey.com", 
                "cambodianews.org", "khpost.com.kh", "cnc.com.kh", "mnb.mn", "montsame.mn", "unuudur.mn", "unen.mn", "mongolnews.mn", "news.mn", "eagle.mn", 
                "gogo.mn", "ikon.mn", "tv5.mn", "mongoltv.mn", "zms.mn", "medee.mn", "olon.mn", "24tsag.mn", "factnews.mn", "news.com.au", "theguardian.com", 
                "smh.com.au", "theage.com.au", "9news.com.au," "heraldsun.com.au", "dailytelegraph.com.au", "theaustralian.com.au", "sbs.com.au", "afr.com", 
                "skynews.com.au", "perthnow.com.au", "couriermail.com.au", "adelaidenow.com.au", "thewest.com.au", "crikey.com.au", "newscorp.com.au", 
                "buzzfeed.com", "independentaustralia.net", "7news.com.au", "10play.com.au", "bdnews24.com", "prothomalo.com", "thedailystar.net", 
                "banglatribune.com", "kalerkantho.com", "jugantor.com", "samakal.com", "banglanews24.com", "dhakatribune.com", "newagebd.net", 
                "daily-sun.com", "ittefaq.com.bd", "tbsnews.net", "thefinancialexpress.com.bd", "channelionline.com", "somoynews.tv", "ntvbd.com", 
                "ekattor.tv", "rtvonline.com", "bangladeshpost.net", "observerbd.com", "bhorerkagoj.com", "dailyjanakantha.com", "protidin.com.bd", 
                "bd-pratidin.com", "sun.mv", "raajje.mv", "avas.mv", "miadhu.mv", "vnews.mv", "psmnews.mv", "edition.mv", "aafathis.mv", "dhauru.com", 
                "haveeru.com.mv", "adhadhu.com", "maldivesindependent.com", "vnexpress.net", "tuoitre.vn", "dantri.com.vn", "24h.com.vn", "vietnamnet.vn", 
                "zingnews.vn", "thanhnien.vn", "baomoi.com", "bongda.com.vn", "thethaovanhoa.vn", "kenh14.vn", "vtc.vn", "nld.com.vn", "timesofindia.indiatimes.com", 
                "hindustantimes.com", "thehindu.com", "indianexpress.com", "ndtv.com", "news18.com", "indiatoday.in", "scroll.in", "thequint.com", 
                "republicworld.com", "zeenews.india.com", "abplive.com", "jagran.com", "bhaskar.com", "amarujala.com", "navbharattimes.indiatimes.com", 
                "lokmat.com", "eenadu.net", "sakshi.com", "manoramaonline.com", "mathrubhumi.com", "economictimes.indiatimes.com", "business-standard.com", 
                "livemint.com", "deccanchronicle.com", "telegraphindia.com", "theprint.in", "livehindustan.com", "indiatvnews.com", "asianetnews.com", 
                "borneobulletin.com.bn", "thescoop.co", "brudirect.com", "mediapermata.com.bn", "pelitabrunei.gov.bn", "rtb.gov.bn", "sultanate.com", 
                "malaysiakini.com", "thestar.com.my", "nst.com.my", "hmetro.com.my", "bharian.com.my", "malaymail.com", "freemalaysiatoday.com", 
                "theedgemarkets.com", "astroawani.com", "sinarharian.com.my", "chinapress.com.my", "sinchew.com.my", "kosmo.com.my", "themalaysianreserve.com", 
                "themalaysianinsight.com", "bernama.com", "vocket.com", "therakyatpost.com", "worldofbuzz.com", "lowyat.net", "malaysiadateline.com", 
                "guampdn.com", "postguam.com", "kuam.com", "mvariety.com", "pacificnewscenter.com", "pbsguam.org", "ktgm.com", "mbjguam.com", 
                "pacificislandtimes.com", "inquirer.net", "philstar.com", "gmanetwork.com", "abs-cbn.com", "rappler.com", "mb.com.ph", "cnnphilippines.com", 
                "sunstar.com.ph", "bworldonline.com", "manilatimes.net", "pna.gov.ph", "tribune.net.ph", "tempo.com.ph", "interaksyon.com", 
                "cebudailynews.inquirer.net", "hetana.ph", "mindanaotimes.com.ph", "visayandailystar.com", "manilastandard.net", "dzrhnews.com.ph", 
                "straitstimes.com", "channelnewsasia.com", "mothership.sg", "todayonline.com", "businesstimes.com.sg", "zaobao.com.sg", "asiaone.com", 
                "tnp.sg", "theindependent.sg", "mustsharenews.com", "thesmartlocal.com", "hardwarezone.com.sg", "onlinecitizenasia.com", "beritaharian.sg", 
                "tamilmurasu.com.sg", "berita.sg", "sgag.sg", "thehoneycombers.com", "eatbook.sg", "vulcanpost.com", "eco-business.com", "8world.com", 
                "news.naver.com", "news.daum.net", "news.nate.com", "en.yna.co.kr", "chosun.com", "joongang.co.kr", "donga.com", "hani.co.kr", 
                "koreaherald.com", "koreatimes.co.kr", "kbs.co.kr", "imbc.com", "sbs.co.kr", "jtbc.joins.com", "ytn.co.kr", "mk.co.kr", "khan.co.kr", 
                "hankookilbo.com", "thebell.co.kr", "ilgan.co.kr", "dispatch.co.kr", "moneys.mt.co.kr", "edaily.co.kr", "detik.com", "kompas.com", 
                "tribunnews.com", "liputan6.com", "cnnindonesia.com", "yahoo.co.id", "okezone.com", "viva.co.id", "tempo.co", "republika.co.id", 
                "merdeka.com", "antaranews.com", "suara.com", "sindonews.com", "bisnis.com", "beritasatu.com", "inews.id", "kumparan.com", 
                "news.yahoo.co.jp", "line.me", "ameblo.jp", "auone.jp", "livedoor.com", "nikkei.com", "yomiuri.co.jp", "asahi.com", "japantimes.co.jp", 
                "mainichi.jp", "tv-asahi.co.jp", "ntv.co.jp", "fujitv.co.jp", "sankei.com", "nikkansports.com", "oricon.co.jp", "excite.co.jp", 
                "huffingtonpost.jp", "diamond.jp", "sanook.com", "thairath.co.th", "khaosod.co.th", "pantip.com", "bangkokpost.com", "matichon.co.th", 
                "kapook.com", "mgronline.com", "komchadluek.net", "dailynews.co.th", "nationthailand.com", "workpointtoday.com", "thaipbs.or.th", 
                "ch3thailand.com", "mthai.com", "springnews.co.th", "trueid.net", "bangkokbiznews.com", "posttoday.com", "prachachat.net"]
    filtered_entries = []
    for entry in feed.entries:
        published = Article.parse_published_parsed(getattr(entry, "published_parsed", None))
        url = decode_google_url(entry.link)
        base_url = str(urlparse(url).netloc)
        base_url = base_url.removeprefix("www.")

        if (base_url in top_urls) and (published and published >= cutoff):
            filtered_entries.append(entry)

    articles = [Article.from_rss_entry(entry) for entry in filtered_entries]

    if limit:
        articles = articles[:limit]

    return articles
