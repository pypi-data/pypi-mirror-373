from collections import Counter
import contextlib
import filecmp
import platform
from pprint import pprint
import tempfile
import time

import unicodedataplus as udp
import pytest

from fontfinder import *


FONT_INSTALL_SLEEP_STEP = 1
MAX_FONT_INSTALL_RETRIES = 20


class TestMode(Enum):
    TEST    = auto()    # Run the test as normal
    CREATE  = auto()    # Create the expected output, rather than testing for it
    OBSERVE = auto()    # Observe output: Use known instead of temp directories, don't unzip word docs, don't test


class FontFinderWithTestFonts(FontFinder):
    def get_test_font_infos(self):
        font_infos = []
        font_infos.append(FontInfo(main_script="Latin", script_variant="Fontfinder", family_name="Fontfinder",
                          subfamily_name="Regular", postscript_name="Fontfinder-Regular", form=FontForm.SANS_SERIF,
                          width=FontWidth.NORMAL, weight=FontWeight.REGULAR, style=FontStyle.UPRIGHT,
                          format=FontFormat.OTF,
                          url="https://github.com/multiscript/fontfinder/raw/main/test/data/Fontfinder-Regular.otf",
                          downloaded_path=Path(__file__, "../data/Fontfinder-Regular.otf").resolve())
                         )
        font_infos.append(FontInfo(main_script="Latin", script_variant="Fontfinder", family_name="Fontfinder",
                          subfamily_name="Bold", postscript_name="Fontfinder-Bold", form=FontForm.SANS_SERIF,
                          width=FontWidth.NORMAL, weight=FontWeight.BOLD, style=FontStyle.UPRIGHT,
                          format=FontFormat.OTF,
                          url="https://github.com/multiscript/fontfinder/raw/main/test/data/Fontfinder-Bold.otf",
                          downloaded_path=Path(__file__, "../data/Fontfinder-Bold.otf").resolve())
                         )
        font_infos.append(FontInfo(main_script="Latin", script_variant="Fontfinder", family_name="Fontfinder",
                          subfamily_name="Italic", postscript_name="Fontfinder-Italic", form=FontForm.SANS_SERIF,
                          width=FontWidth.NORMAL, weight=FontWeight.REGULAR, style=FontStyle.ITALIC,
                          format=FontFormat.OTF,
                          url="https://github.com/multiscript/fontfinder/raw/main/test/data/Fontfinder-Italic.otf",
                          downloaded_path=Path(__file__, "../data/Fontfinder-Italic.otf").resolve())
                         )
        font_infos.append(FontInfo(main_script="Latin", script_variant="Fontfinder", family_name="Fontfinder",
                          subfamily_name="Bold Italic", postscript_name="Fontfinder-BoldItalic",
                          form=FontForm.SANS_SERIF, width=FontWidth.NORMAL, weight=FontWeight.BOLD,
                          style=FontStyle.ITALIC, format=FontFormat.OTF,
                          url="https://github.com/multiscript/fontfinder/raw/main/test/data/Fontfinder-BoldItalic.otf",
                          downloaded_path=Path(__file__, "../data/Fontfinder-BoldItalic.otf").resolve())
                         )
        return font_infos
    
    def known_fonts(self, filter_func = None):
        if self._all_known_fonts is None:
            # Add our test fonts to the cached collection
            super().known_fonts(filter_func)
            assert self._all_known_fonts is not None
            self._all_known_fonts.extend(self.get_test_font_infos())
        return super().known_fonts(filter_func)


class TestFontFinder:
    def get_test_font_info(self):
        font_info = FontInfo(main_script="Latin", family_name="Fontfinder", subfamily_name="Regular",
                             postscript_name="Fontfinder-Regular", form=FontForm.SANS_SERIF,
                             width=FontWidth.NORMAL, weight=FontWeight.REGULAR, style=FontStyle.UPRIGHT,
                             format=FontFormat.OTF,
                             url="https://github.com/multiscript/fontfinder/raw/main/test/data/Fontfinder-Regular.otf",
                             downloaded_path=Path(__file__, "../data/Fontfinder-Regular.otf").resolve()
                             )
        return font_info

    def test_attr_contains_str(self):
        filter = attr_contains_str("family_name", ["mono", "display"])
        assert filter(FontInfo(family_name="Some Font Mono"))
        assert filter(FontInfo(family_name="Some Display Font"))
        assert not filter(FontInfo(family_name="Some Font UI"))

    def test_attr_not_contains_str(self):
        filter = attr_not_contains_str("family_name", ["mono", "display"])
        assert not filter(FontInfo(family_name="Some Font Mono"))
        assert not filter(FontInfo(family_name="Some Display Font"))
        assert filter(FontInfo(family_name="Some Font UI"))

    def test_known_fonts(self):
        ff = FontFinder()
        font_infos = ff.known_fonts() # Ensure no errors in creating list
        # font_infos = [font for font in font_infos if font.family_name == "Noto Sans"]
        # print(len(fonts))
        # pprint(fonts[-10:])

    def test_known_scripts(self):
        ff = FontFinder()
        pprint(ff.known_scripts())

    def test_known_script_variants(self):
        ff = FontFinder()
        script_variants = ff.known_script_variants() # Ensure no errors
    
    def test_all_unicode_scripts(self):
        ff = FontFinder()
        pprint(ff.all_unicode_scripts())

    def test_scripts_not_known(self):
        ff = FontFinder()
        print("Unicode Scripts Not Covered:")
        scripts_not_known = ff.scripts_not_known()
        pprint(scripts_not_known)
        assert scripts_not_known == ['Garay', 'Gurung_Khema', 'Kirat_Rai', 'Ol_Onal', 'Todhri', 'Tulu_Tigalari']
                                    # These are new scripts in Unicode 16, not yet covered by Noto fonts.
        print("Noto Pseudo-Scripts Not in Unicode:")
        not_in_unicode = list(set(ff.known_scripts()) - set(ff.all_unicode_scripts()) - {''})
        print(not_in_unicode)
        assert len(not_in_unicode) == 0

    def test_analyse(self):
        ff = FontFinder()
        for sample_text in sample_texts:
            text_info = ff.analyse(sample_text['text'])
            assert sample_text['main_script'] == text_info.main_script
            assert sample_text['script_variant'] == text_info.script_variant

    def test_empty_text(self):
        ff = FontFinder()
        text_info = ff.analyse('')
        assert text_info.main_script == ''
        assert text_info.script_variant == ''
        assert text_info.emoji_count == 0
        assert len(text_info.script_count) == 0

        assert ff.find_families(text_info) == []
        assert ff.find_family(text_info) == None

        assert ff.find_families('') == []
        assert ff.find_family('') == None

    def test_find_families(self):
        ff = FontFinder()
        for sample_text in sample_texts:
            family_names = ff.find_families(sample_text['text'])
            assert sample_text['expected_family_names'] == family_names

    def test_find_family(self):
        ff = FontFinder()
        for sample_text in sample_texts:
            family_name = ff.find_family(sample_text['text'])
            assert sample_text['expected_family_name'] == family_name

    def test_find_family_fonts(self):
        ff = FontFinder()
        print("Finding family members")
        font_infos = ff.find_family_fonts("Noto Naskh Arabic")
        fullnames = {font_info.fullname for font_info in font_infos}
        assert fullnames == {'Noto Naskh Arabic Bold', 'Noto Naskh Arabic Medium',
                            'Noto Naskh Arabic Regular', 'Noto Naskh Arabic SemiBold'}
    
    def test_find_multiple_family_fonts(self):
        ff = FontFinder()
        family_1 = "Noto Naskh Arabic"
        family_2 = "Noto Sans Cherokee"

        font_infos_1 = ff.find_family_fonts(family_1)
        fullnames_1 = {font_info.fullname for font_info in font_infos_1}
        assert len(fullnames_1) > 0

        font_infos_2 = ff.find_family_fonts(family_2)
        fullnames_2 = {font_info.fullname for font_info in font_infos_2}
        assert len(fullnames_2) > 0
        assert fullnames_1 != fullnames_2

        font_infos_combo = ff.find_family_fonts([family_1, family_2])
        fullnames_combo = {font_info.fullname for font_info in font_infos_combo}
        assert fullnames_combo == fullnames_1 | fullnames_2

    def test_find_empty_family_fonts(self):
        ff = FontFinder()
        font_infos = ff.find_family_fonts([])
        assert font_infos == []

        font_infos = ff.find_family_fonts([], "Latin")
        assert font_infos == []

    def test_all_installed_families(self):
        ff = FontFinder()
        all_installed_families = ff.all_installed_families()
        pprint(all_installed_families)

    def test_known_fonts_to_csv(self, test_mode = TestMode.TEST):
        ff = FontFinder()
        font_infos = ff.known_fonts()
        filename = "known_fonts.csv"
        self._font_infos_test_to_csv(font_infos, filename, test_mode)

    def test_script_variants_to_csv(self, test_mode = TestMode.TEST):
        ff = FontFinder()
        font_infos = []
        for (main_script, script_variant) in ff.known_script_variants():
            print(f"{main_script}, {script_variant}")
            font_family = ff.find_family(TextInfo(main_script, script_variant))
            print(font_family)
            assert font_family is not None
            font_infos.extend(ff.find_family_fonts(font_family, main_script, script_variant))
        filename = "known_script_variants.csv"
        self._font_infos_test_to_csv(font_infos, filename, test_mode)

    def _font_infos_test_to_csv(self, font_infos, filename, test_mode):
        if test_mode is TestMode.TEST:
            context_manager = tempfile.TemporaryDirectory()
        elif test_mode is TestMode.OBSERVE:
            dir_path = Path("~/Desktop/TestFontFinder/").expanduser()
            dir_path.mkdir(parents=True, exist_ok=True)
            context_manager = contextlib.nullcontext(dir_path)
        else:
            assert False

        write_fonts = font_infos

        with context_manager as output_dir:
            csv_path = Path(output_dir, filename)
            write_font_infos_to_csv(write_fonts, csv_path)
            read_fonts = read_font_infos_from_csv(csv_path)
        
        # for item in zip(write_fonts, read_fonts):
        #     if item[0] != item[1]:
        #         print(item[0])
        #         print(item[1])
        #         assert False
        assert write_fonts == read_fonts

    def test_download_fonts(self, test_mode = TestMode.TEST):
        ff = FontFinderWithTestFonts()
        test_font_infos = ff.get_test_font_infos()
        temp_dir = None
        download_dir = None
        if test_mode is TestMode.TEST:
            temp_dir = tempfile.TemporaryDirectory()
            download_dir = temp_dir.name
        elif test_mode is TestMode.OBSERVE:
            download_dir = Path("~/Desktop/TestFontFinder/Download").expanduser()
            download_dir.mkdir(parents=True, exist_ok=True)

        assert download_dir is not None
        ff.download_fonts(test_font_infos, download_dir)
        filenames = [font_info.filename for font_info in test_font_infos]
        cmp_result = filecmp.cmpfiles(download_dir, Path(__file__, "../data").resolve(), filenames,
                                      shallow=False)
        if temp_dir is not None:
            temp_dir.cleanup()
        assert cmp_result[1] == []
        assert cmp_result[2] == []

    def test_install_fonts(self):
        print("Uninstalling fonts")
        ff = FontFinderWithTestFonts()
        test_font_infos = ff.get_test_font_infos()
        self.uninstall_fonts_and_verify(ff, test_font_infos)

        print("Installing fonts")
        ff = FontFinderWithTestFonts()
        test_font_infos = ff.get_test_font_infos()
        self.install_fonts_and_verify(ff, test_font_infos)

        print("Uninstalling fonts")
        ff = FontFinderWithTestFonts()
        test_font_infos = ff.get_test_font_infos()
        self.uninstall_fonts_and_verify(ff, test_font_infos)

    def test_full_test(self):
        ff = FontFinderWithTestFonts()
        self.uninstall_fonts_and_verify(ff, ff.get_test_font_infos())

        text_info = TextInfo("Latin", "Fontfinder")
        font_family = ff.find_family(text_info)
        assert font_family == "Fontfinder"

        font_infos = ff.find_family_fonts(font_family)
        assert font_infos == ff.get_test_font_infos()

        font_infos = ff.find_family_fonts_to_download(font_family)
        assert font_infos == ff.get_test_font_infos()

        temp_dir = tempfile.TemporaryDirectory()
        font_infos = ff.download_fonts(font_infos, temp_dir.name)
        self.install_fonts_and_verify(ff, font_infos)
        temp_dir.cleanup()

        expect_empty = ff.find_family_fonts_to_download(font_family)
        assert len(expect_empty) == 0

        self.uninstall_fonts_and_verify(ff, font_infos)

    def test_is_rtl(self):
        ff = FontFinder()
        assert not ff.is_rtl("Latin")
        assert ff.is_rtl("Arabic")
        assert ff.is_rtl("Hebrew")

        for sample_text in sample_texts:
            text_info = ff.analyse(sample_text['text'])
            assert sample_text['is_rtl'] == ff.is_rtl(text_info)
    
    def test_is_rtl_empty_text(self):
        ff = FontFinder()
        assert ff.is_rtl('blah') == False
        assert ff.is_rtl(ff.analyse('')) == False

    def install_fonts_and_verify(self, font_finder, font_infos):
        font_finder.install_fonts(font_infos)
        font_families = []
        for i in range(MAX_FONT_INSTALL_RETRIES):
            time.sleep(FONT_INSTALL_SLEEP_STEP)
            font_families = font_finder.all_installed_families()
            if font_infos[0].family_name in font_families:
                break
        assert font_infos[0].family_name in font_families

    def uninstall_fonts_and_verify(self, font_finder, font_infos):
        try:
            font_finder.uninstall_fonts(font_infos)
        except FileNotFoundError:
            pass
        font_families = [font_infos[0].family_name]
        for i in range(MAX_FONT_INSTALL_RETRIES):
            time.sleep(FONT_INSTALL_SLEEP_STEP)
            font_families = font_finder.all_installed_families()
            if font_infos[0].family_name not in font_families:
                break
        assert font_infos[0].family_name not in font_families

    def test_unihan_generation(self):
        import unihan_etl.core
        selected_fields = ('kTraditionalVariant', 'kSimplifiedVariant')

        with tempfile.TemporaryDirectory() as full_unihan_dir:
            full_unihan_path = Path(full_unihan_dir, "full_unihan.json").resolve()

            with tempfile.TemporaryDirectory() as work_dir:
                packager_options = {
                    "destination": str(full_unihan_path),
                    "work_dir": work_dir,
                    "format": "json",
                    "cache": False,
                    "fields": selected_fields
                }
                packager = unihan_etl.core.Packager(packager_options)
                packager.download()
                packager.export()


    @pytest.mark.skip("Investigation test to examine variants with multiple families")
    def test_multi_family_script_variants(self):
        ff = FontFinder()
        for (main_script, script_variant) in ff.known_script_variants():
            font_families = ff.find_families(TextInfo(main_script, script_variant))
            if len(font_families) > 1:
                print(f"{main_script}, {script_variant}:")
                print(font_families)

    @pytest.mark.skip("Investigation test to examine script of emoji codepoints")
    def test_script_of_emoji(self):
        script_counter = Counter()
        for i in range(0x10ffff):
            char = chr(i)
            if udp.is_emoji_presentation(char) or udp.is_extended_pictographic(char):
                script_counter[udp.script(char)] += 1
        print(script_counter)

#
# These sample texts are taken from the Wikipedia article for 'Earth' in various languages.
#
sample_texts = [
{'language': 'English',
 'main_script': 'Latin',
 'script_variant': '',
 'expected_family_names': ['Noto Sans', 'Noto Sans Mono', 'Noto Serif', 'Noto Serif Display'],
 'expected_family_name': 'Noto Sans',
 'is_rtl': False,
 'text':
'''
Earth is the third planet from the Sun and the only place known in the universe where life has originated and found
habitability. While Earth may not contain the largest volumes of water in the Solar System, only Earth sustains
liquid surface water, extending over 70.8% of the planet with its ocean, making it an ocean world. The polar
regions currently retain most of all other water with large sheets of ice covering ocean and land, dwarfing Earth's
groundwater, lakes, rivers and atmospheric water. The other 29.2% of the Earth's surface is land, consisting of
continents and islands, and is widely covered by vegetation. Below the planet's surface lies the crust, consisting
of several slowly moving tectonic plates, which interact to produce mountain ranges, volcanoes, and earthquakes.
Inside the Earth's crust is a liquid outer core that generates the magnetosphere, deflecting most of the
destructive solar winds and cosmic radiation.

Earth has a dynamic atmosphere, which sustains Earth's surface conditions and protects it from most meteoroids and
UV-light at entry. It has a composition of primarily nitrogen and oxygen. Water vapor is widely present in the
atmosphere, forming clouds that cover most of the planet. The water vapor acts as a greenhouse gas and, together
with other greenhouse gases in the atmosphere, particularly carbon dioxide (CO2), creates the conditions for both
liquid surface water and water vapor to persist via the capturing of energy from the Sun's light. This process
maintains the current average surface temperature of 14.76 °C, at which water is liquid under atmospheric pressure.
Differences in the amount of captured energy between geographic regions (as with the equatorial region receiving
more sunlight than the polar regions) drive atmospheric and ocean currents, producing a global climate system with
different climate regions, and a range of weather phenomena such as precipitation, allowing components such as
nitrogen to cycle.

Earth is rounded into an ellipsoid with a circumference of about 40,000 km. It is the densest planet in the Solar
System. Of the four rocky planets, it is the largest and most massive. Earth is about eight light-minutes away from
the Sun and orbits it, taking a year (about 365.25 days) to complete one revolution. The Earth rotates around its
own axis in slightly less than a day (in about 23 hours and 56 minutes). The Earth's axis of rotation is tilted
with respect to the perpendicular to its orbital plane around the Sun, producing seasons. Earth is orbited by one
permanent natural satellite, the Moon, which orbits Earth at 384,400 km (1.28 light seconds) and is roughly a
quarter as wide as Earth. Through tidal locking, the Moon always faces the Earth with the same side, which causes
tides, stabilizes Earth's axis, and gradually slows its rotation.

Earth, like most other bodies in the Solar System, formed 4.5 billion years ago from gas in the early Solar System.
During the first billion years of Earth's history, the ocean formed and then life developed within it. Life spread
globally and has been altering Earth's atmosphere and surface, leading to the Great Oxidation Event two billion
years ago. Humans emerged 300,000 years ago, and reached a population of 8 billion on November 15, 2022. Humans
depend on Earth's biosphere and natural resources for their survival, but have increasingly impacted the planet's
environment. Humanity's current impact on Earth's climate and biosphere is unsustainable, threatening the
livelihood of humans and many other forms of life, and causing widespread extinctions.[24]
'''},

{'language': 'Chinese (Simplified)',
 'main_script': 'Han',
 'script_variant': 'zh-Hans',
 'expected_family_names': ['Noto Sans CJK SC', 'Noto Serif CJK SC'],
 'expected_family_name': 'Noto Sans CJK SC',
 'is_rtl': False,
 'text':
'''
地球是太阳系中由內及外的第三顆行星，距离太阳149 597 870.7公里/1天文單位，是宇宙中人類已知唯一存在生命的天体[3]，也
是人類居住的星球，共有80億人口[22]。其質量约为5.97×1024公斤，半径约6,371公里，平均密度5.5 g/cm3，是太阳系行星中最高
的。地球同时进行自转和公转运动，分别产生了昼夜及四季的变化更替，一太陽日自转一周，一太陽年公转一周。自转轨道面称为
赤道面，公转轨道面称为黄道面，两者之间的夹角称为黄赤交角。地球仅有一顆自然卫星，即月球。

地球表面有71%的面积被水覆盖，称为海洋或湖或河流[23][24]，其余是陆地板块組成的大洲和岛屿，表面分布河流和湖泊等水源。
南极的冰盖及北极存有冰。主體包括岩石圈、地幔、熔融态金属的外地核以及固态金属的內地核。擁有由外地核產生的地磁场
[25]。外部被氣體包圍，称为大氣層，主要成分為氮、氧、二氧化碳、氬。

地球诞生于约45.4亿年前[26][27][28][29]，42億年前開始形成海洋[30][31]，并在35亿年前的海洋中出现生命
[32][33][34][35][36]，之后逐步涉足地表和大气，并分化为好氧生物和厌氧生物。早期生命迹象产生的具體证据包括格陵兰岛西
南部变质沉积岩中拥有约37亿年的历史的生源石墨，以及澳大利亚大陆西部岩石中约41亿年前的早期生物遗骸[37][38]。此后除去
数次生物集群灭绝事件，生物种类不断增多[39]。根据科学界测定，地球曾存在过的50亿种物种中[40]，已经绝灭的占约
99%[41][42]，据统计，现今存活的物种大约有1,200至1,400万个[43][44]，其中有记录证实存活的物种120万个，而余下的86%尚未
被正式发现[45]。2016年5月，有科学家认为现今地球上大概共出现过1万亿种物种，其中人类正式发现的仅占十万分之一
[46]。2016年7月，研究团队在研究现存生物的基因后推断所有现存生物的共祖中共存在有355种基因[47][48]。地球上有约80.3亿
人口[49]，分成了约200个国家和地区，藉由外交、旅游、贸易、传媒或战争相互联系[50]。
'''},

{'Language': 'Cantonese',
 'main_script': 'Han',
 'script_variant': 'zh-Hant',
 'expected_family_names': ['Noto Sans CJK TC', 'Noto Serif CJK TC'],
 'expected_family_name': 'Noto Sans CJK TC',
 'is_rtl': False,
 'text':
'''
佢距離太陽 1.5 億公里（1個天文單位）遠，係太陽系嘅行星入面第三近太陽嘅－排正喺水星同金星之後。佢嘅質量係 5.97 ×
1024 公斤左右，半徑大約係 6371 公里，密度係每立方厘米 5.514 克。如果齋由大細嚟睇，佢喺太陽系嘅行星入面排第五，係太
陽系嘅類地行星（Terrestrial planet；指主要由石頭構成嘅行星）入面最大粒嘅；同時佢係太陽系入面密度最高嘅行星[2]。同其
他行星一樣，地球會自轉同公轉：佢大約每廿四個鐘頭會自轉一個圈（為之一日），每 365.26 日會圍住太陽公轉一個圈（為之一
個太陽年）。佢嘅自轉產生咗晝夜，而公轉就產生咗一年嘅四季。同時，地球有粒自然衛星－月球－圍住佢轉[2]。

地球嘅表面有 71% 嘅面積俾水𢫏住－呢啲面積包括咗海、河、同埋湖呀噉[2][3]，淨低嘅係由陸地板塊（Tectonic plate）組成嘅
各個大陸同埋島。兩極地區大部份地方長年俾冰覆蓋。地球嘅內部分做外地核同內地核兩層，前者由熔化咗嘅金屬組成，而後者由
固體嘅金屬組成[4]。喺地球嘅最外層，有一浸氣體包住－即係所謂嘅大氣層。大氣層嘅主要成分係氮（Nitrogen）同氧（Oxygen）
呢兩種元素。

地球係目前成個宇宙入面已知嘅行星當中唯一一個有生命存在嘅，而且佢仲係智人（Homo sapien）嘅屋企。佢喺大約 45 億 4 千
萬年前形成[2][5]，而月球就係喺之後嘅 1 千萬年開始圍住佢轉。地球形成咗 10 億年之後左右開始有生命體[6][7]，而隨住生物
嘅進化[8][9]，佢今日已經住咗各種各樣嘅生物，有各種嘅動物同植物－即係有生物多樣性（Biodiversity）[8][10]。

根據對化石同基因嘅研究，現代嘅人類喺大概 500 萬至 700 萬年之前出現，而且同現代嘅黑猩猩係近親。到咗廿一世紀初，地球
上大約有 74 億人口[11]。聯合國估話會愈嚟愈多。人類有得分做黃種人、白人、同埋黑人等多個人種，而呢柞人種入面又有啲亞
種[9]－例如係黃種人，就有得分做漢族同大和族等，而漢族仲有得細分類做包括粵人在內嘅各個民系－人類喺文化同血統上都好多
樣化。
'''},

{'language': 'Arabic',
 'main_script': 'Arabic',
 'script_variant': '',
 'expected_family_names': ['Noto Kufi Arabic', 'Noto Naskh Arabic', 'Noto Naskh Arabic UI', 'Noto Sans Arabic',
                           'Noto Sans Arabic UI'],
 'expected_family_name': 'Noto Naskh Arabic',
 'is_rtl': True,
 'text':
'''
الأَرْض (رمزها: 🜨) هي ثالث كواكب المجموعة الشمسية بعدًا عن الشمس بعد عطارد والزهرة، وتُعتبر من أكبر الكواكب
الأرضية وخامس أكبر الكواكب في النظام الشمسي، وذلك من حيث قطرها وكتلتها وكثافتها، ويُطلق على هذا الكوكب أيضًا اسم
العالم.

تعتبر الأرض مسكنًا لملايين الأنواع  من الكائنات الحية، بما فيها الإنسان؛ وهي المكان الوحيد المعروف بوجود حياة عليه
في الكون. تكونت الأرض منذ حوالي 4.54 مليار سنة، وقد ظهرت الحياة على سطحها في المليار سنة الأخيرة. ومنذ ذلك الحين
أدى الغلاف الحيوي للأرض إلى تغير الغلاف الجوي والظروف غير الحيوية الموجودة على الكوكب، مما سمح بتكاثر الكائنات التي
تعيش فقط في ظل وجود الأكسجين وتكوّن طبقة الأوزون، التي تعمل مع المجال المغناطيسي للأرض على حجب الإشعاعات الضارة،
مما يسمح بوجود الحياة على سطح الأرض. تحجب طبقة الأوزون الأشعة فوق البنفسجية، ويعمل المجال المغناطيسي للأرض على
إزاحة وإبعاد الجسيمات الأولية المشحونة القادمة من الشمس بسرعات عظيمة ويبعدها في الفضاء الخارجي بعيدا عن الأرض، فلا
تتسبب في الإضرار بالكائنات الحية.

أدت الخصائص الفيزيائية للأرض والمدار الفلكي المناسب التي تدور فيه حول الشمس حيث تمدها بالدفء والطاقة ووجود الماء
إلى نشأة الحياة واستمرار الحياة عليها حتى العصر الحالي، ومن المتوقع أن تستمر الحياة على الأرض لمدة 1.2 مليارات عام
آخر، يقضي بعدها ضوء الشمس المتزايد على الغلاف الحيوي للأرض، حيث يعتقد العلماء بأن الشمس سوف ترتفع درجة حرارتها في
المستقبل وتتمدد وتكبر حتى تصبح عملاقا أحمرا ويصل قطرها إلى كوكب الزهرة أو حتى إلى مدار الأرض، على نحو ما يروه من
تطور للنجوم المشابهة للشمس في الكون عند قرب انتهاء عمر النجم ونفاذ وقوده من الهيدروجين. عندئذ تنهي حرارة الشمس
المرتفعة الحياة على الأرض. هذا إذا لم يحدث لها حدث كوني آخر قبل ذلك - كانفجار نجم قريب في هيئة مستعر أعظم - ينهي
الحياة عليها.

يعيش أكثر من 8 مليار شخص على الأرض، وتعمل موارد الأرض المختلفة على إبقاء جمهرة عالمية ضخمة من البشر، الذين يقتسمون
العالم فيما بينهم ويتوزعون على حوالي 200 دولة مستقلة، وطوّر البشر مجتمعات وحضارات وثقافات متنوعة، ويتفاعلون مع
بعضهم البعض بأساليب متنوعة تشمل التواصل الدبلوماسي السياحة التجارة والقتال العسكري أيضًا. ظهر في الثقافة البشرية
نظريات وتمثيلات مختلفة للأرض، فبعض الحضارات القديمة جسدتها كإلهة، والبعض اعتقدها مسطحة، وقال آخرون أنها مركز الكون،
والمعتقد السائد حاليًا ينص على أن هذا الكوكب هو عبارة عن بيئة متكاملة تتطلب إشراف الإنسان عليها لصيانتها من الأخطار
التي تهددها، والتي من شأنها أن تهدد الإنسان نفسه في نهاية المطاف.
'''},

{'language': 'Japanese',
 'main_script': 'Han',
 'script_variant': 'ja',
 'expected_family_names': ['Noto Sans CJK JP', 'Noto Serif CJK JP'],
 'expected_family_name': 'Noto Sans CJK JP',
 'is_rtl': False,
 'text':
'''
地球とは人類が住んでいる天体、つまり人類の足元にある天体のことである。「地」という字・概念と「球」という字・概念で
それを表現している。英語（Earth）やラテン語 （Tellus, Terra）など他の言語でも多くは「大地」を表す語が当てられてい
る。日本語において、この星を呼ぶ名である「地球」という単語は、中国語由来である。中国語の「地球」は明朝の西学東漸
（中国語版）期に初めて見られ、イタリア人宣教師マテオ・リッチ（1552年 - 1610年）の『坤輿万国全図』がこの単語が使用さ
れた最初期の資料である[7][8]。清朝後期に西洋の近代科学が中国に入ってくると、大地球体説が中国の人々によって次第に受
け入れられるようになり、「地球」（または地毬）という単語が広く使われるようになった[9][10][11]。当時の新聞申報の創刊
号には「地球説」に関する文章が掲載されている[12]。日本では、江戸時代頃にこの漢語が輸入され、1700年代頃の西洋紀聞や
和漢三才図会に、使用例がある。幕末から明治期には、庶民も使うほどまでに定着した[13][14][15]。

地球は太陽系の惑星の一つである[5]。その形は、ほぼ回転楕円体で、赤道の半径は6378kmほどで、極半径は6357km[5]。（より
精度の高い数字については後述の「物理的性質」の項を参照のこと）その運動に着目すると、365日強で太陽の周囲を一周し、24
時間で1回 自転しており[5]、太陽からの平均距離は1億4960万km[1]。

その内部は大まかに地殻、マントル、核の3部分から成っている。地球全体の平均密度は1cm3当たり5.51gである[1]。表面は大気
に覆われている[5]。

放射性元素による隕石の年代測定と[16]、アポロ計画によって持ち帰られた月の岩石分析から[17]、地球は誕生してから約46億
年経過していると推定される[18]。

太陽系の年齢もまた隕石の年代測定に依拠するので、地球は太陽系の誕生とほぼ同時に形成されたとしてよい。10個程度の火星
サイズの原始惑星の衝突合体によって形成されたと考えられている[19]。

太陽系内の惑星としては、太陽から2天文単位内の位置に存在し、岩石質外層と鉄を主成分とする中心核を持つ「地球型惑星」に
分類され[20]、太陽系の地球型惑星の中で大きさ、質量、密度ともに最大のものである。


水平線を超えて海面に隠れる船組成は地表面からの深さによって異なる。地殻に存在する元素は、酸素（質量比49.5%）とケイ素
（同25.8%）が主体で、以下アルミニウム・鉄・カルシウム・ナトリウム・カリウム・マグネシウムなどの金属元素が含まれる。
この元素別質量百分率はクラーク数として纏められている[21]。ほとんどはケイ酸塩など金属酸化物の形で存在する[21]。

対照的に、中心部分は鉄やニッケルが主体である。地表面の71.1%は液体の水（海）で被われており[22]、地表から上空約100km
までの範囲には窒素・酸素を主成分とする大気がある。大気の組成は高度によって変化する。

地球はほぼ球形であるため、海抜0mの地表面に立った人が一度に見渡せる範囲は水平線が生じる半径3km〜5kmの円の内側に限ら
れる。分かりやすい事例として、遠方に向かって航行する船，長い直線形の橋，水面に立つ送電用鉄塔の列は、水平線に近づく
と下方に沈み込み、海面に隠れてしまうことが挙げられる。また、電離層や通信衛星や中継回線を用いない無線通信にも、水平
線までの見通し距離内でしか通信出来ないと言う制約が生じる。さらに、緯度が変わると夜間に見える天体に違いが発生する。
地球が球体である証拠は生身の人間には実感しにくいため、かつては地球平面説が信じられたこともあった。
'''},

{'language': 'Korean',
 'main_script': 'Hangul',
 'script_variant': '',
 'expected_family_names': ['Noto Sans CJK KR', 'Noto Serif CJK KR'],
 'expected_family_name': 'Noto Sans CJK KR',
 'is_rtl': False,
 'text':
'''
지구(地球, 영어: Earth)는 태양으로부터 세 번째 행성이며, 조금 두꺼운 대기층으로 둘러싸여 있고, 지금까지 발견된
지구형 행성 가운데 가장 크다. 지구는 45억 6700만 년 전 형성되었으며, 용암 활동이 활발했던 지구와 행성 테이아의
격렬한 충돌로 생성되었을 달을 위성으로 둔다. 지구의 중력은 우주의 다른 물체, 특히 태양과 지구의 유일한 자연위성인
달과 상호작용한다. 지구와 달 사이의 중력 작용으로 조석 현상이 발생한다.

지구의 역사 지구의 형성 과정 지구는 약 45억년 전에 형성되었으며, 태양계가 형성되던 시점과 때를 같이한다. 원시
태양계 원반의 태양 가까운 부분에서는 갓 방출되기 시작한 태양의 복사에너지에 의해 휘발성 성분이 제거되면서 규소를
주성분으로 하는 암석 종류와 철, 니켈 등의 금속성분이 남게 된다. 이들은 원시 태양 주위를 공전하면서 합쳐서 그 크기를
불리게 되는데, 어느 정도 몸집과 중력을 가진 것들을 미행성이라고 부른다. 미행성들은 보다 작은 소행성이나 성간 물질을
유인하여 성장하였다. 미행성의 크기가 커지면 성장속도는 가속된다. 크기가 작은 소행성들이 충돌하게 되면 충돌의
충격으로 조각들이 흩어지게 되나, 크기가 큰 것들이 충돌하게 되면 중력이 강하기 때문에 탈출하는 조각들을 회수할 수
있기 때문이다. 이때 생긴 미행성들 중에서 현재까지 남아 있는 것은 5개이다.

원시 지구는 바깥부분이 거의 완전히 녹은 상태를 경험하게 되면서 성장한다. 원시 지구의 열원은 크게 3가지로 설명할 수
있으며, 첫 번째는 소행성의 충돌이다. 소행성의 충돌은 운동에너지를 열에너지로 바꾸어 원시 지구를 뜨겁게 가열했다.
다른 하나는 중력 에너지이다. 원시지구가 충돌로 인한 가열 때문에 조금씩 녹기 시작하자 그 때까지 뒤섞여 있던 철과
규소가 중력에 의해서 서로 분리되기 시작한 것이다. 무거운 철이 중력에너지가 낮은 지구 중심으로 쏠려 내려가면서
굉장한 중력에너지를 열에너지의 형태로 방출한다. 세 번째 열원은 원시 태양계에 충만하던 방사성 동위원소의 붕괴열이다.
지구의 바깥부분이 완전히 녹은 상태를 마그마 바다라고 한다. 마그마 바다의 깊이는 수백 km에 달했다고 여겨진다. 중력
분화가 끝나고,낙하할 소행성들도 거의 정리가 되자 지구는 식기 시작한다. 마그마 바다가 식기 시작하면서 최초의 지각이
형성된다.

대기와 바다의 형성 지구 대기의 역사는 암석과 마그마로부터 방출된 기체들이 지구 주위에 중력으로 묶이면서 시작된다.
이렇게 형성된 대기를 원시 대기라고 한다. 원시 대기를 이루는 물질은 지구를 형성한 소행성과 혜성 따위에 포함되어있던
휘발성 물질로부터 비롯되었다. 지구가 식어가면서 마그마 바다가 식어 고체의 바닥이 다시 형성되고, 혜성에 들어있던
미량의 물은 많은 양의 혜성이 떨어지면서 축적되기 시작했고, 마그마가 식어 고체의 바닥이 형성된 후에 원시 대기의
수증기 성분이 응결하여 비가 내리기 시작하였다. 이 비는 원시 바다를 형성하였다. 이때 땅과 대기에 있던 염분들이 비에
의해 바다로 녹아들어 가면서 바다가 짜게 되었고 소금을 얻을 수 있게 되었다.
'''},

{'language': 'Hindi',
 'main_script': 'Devanagari',
 'script_variant': '',
 'expected_family_names': ['Noto Sans Devanagari', 'Noto Serif Devanagari'],
 'expected_family_name': 'Noto Sans Devanagari',
 'is_rtl': False,
 'text':
'''
पृथ्वी (प्रतीक: 🜨) सौर मण्डल में सूर्य से तीसरा ग्रह है और एकमात्र खगोलीय वस्तु है जो जीवन को आश्रय देने के लिए
जाना जाता है। इसकी सतह का 71% भाग जल से तथा 29% भाग भूमि से ढका हुआ है। इसकी सतह विभिन्न प्लेटों से बनी हुए है। इस
पर जल तीनो अवस्थाओं में पाया जाता है। इसके दोनों ध्रुवों पर बर्फ की एक मोटी परत है।

रेडियोमेट्रिक डेटिंग अनुमान और अन्य सबूतों के अनुसार पृथ्वी की उत्पत्ति 4.54 अरब साल पहले हुई थी। पृथ्वी के इतिहास
के पहले अरब वर्षों के भीतर जीवों का विकास महासागरों में हुआ और पृथ्वी के वायुमण्डल और सतह को प्रभावित करना शुरू कर
दिया जिससे अवायुजीवी और बाद में, वायुजीवी जीवों का प्रसार हुआ। कुछ भूगर्भीय साक्ष्य इंगित करते हैं कि जीवन का आरम्भ
4.1 अरब वर्ष पहले हुआ होगा। पृथ्वी पर जीवन के विकास के दौरान जैवविविधता का अत्यन्त विकास हुआ। हजारों प्रजातियाँ
लुप्त होती गयी और हजारों नई प्रजातियाँ उत्पन्न हुई। इसी क्रम में पृथ्वी पर रहने वाली 99% से अधिक प्रजातियाँ विलुप्त
हैं। सूर्य से उत्तम दूरी, जीवन के लिए उपयुक्त जलवायु और तापमान ने जीवों में विविधता को बढ़ाया।

पृथ्वी का वायुमण्डल कई परतों से बना हुआ है। नाइट्रोजन और ऑक्सीजन की मात्रा सबसे अधिक है। वायुमण्डल में ओज़ोन गैस की
एक परत है जो सूर्य से आने वाली हानिकारक पराबैंगनी किरणों को रोकती है। वायुमण्डल के घने होने से इस सूर्य का प्रकाश
कुछ मात्रा में प्रवर्तित हो जाता है जिससे इसका तापमान नियन्त्रित रहता है। अगर कोई उल्का पिण्ड पृथ्वी के वायुमण्डल
में प्रवेश कर जाता है तो वायु के घर्षण के कारण या तो जल कर नष्ट हो जाता है या छोटे टुकड़ों में विभाजित हो जाता है।

पृथ्वी की ऊपरी सतह कठोर है। यह पत्थरों और मृदा से बनी है। पृथ्वी का भूपटल कई कठोर खण्डों या विवर्तनिक प्लेटों में
विभाजित है जो भूगर्भिक इतिहास के दौरान एक स्थान से दूसरे स्थान को विस्थापित हुए हैं। इसकी सतह पर विशाल पर्वत, पठार,
महाद्वीप, द्वीप, नदियाँ, समुद्र आदि प्राकृतिक सरंचनाएँ है। पृथ्वी की आन्तरिक रचना तीन प्रमुख परतों में हुई है
भूपटल, भूप्रावार और क्रोड। इसमें से बाह्य क्रोड तरल अवस्था में है और एक ठोस लोहे और निकल के आतंरिक कोर के साथ
क्रिया करके पृथ्वी मे चुम्बकत्व या चुम्बकीय क्षेत्र को पैदा करता है। पृथ्वी का चुम्बकीय क्षेत्र विभिन्न प्रकार के
आवेशित कणों को प्रवेश से रोकता है।

पृथ्वी सूर्य से लगभग 15 करोड़ किलोमीटर दूर स्थित है। दूरी के आधार पर यह सूर्य से तीसरा ग्रह है। यह सौर मण्डल का
सबसे बड़ा चट्टानी पिण्ड है। पृथ्वी सूर्य का एक चक्कर 365 दिनों में पूरा करती है। यह अपने अक्ष पर लम्बवत 23.5 डिग्री
झुकी हुई है। इसके कारण इस पर विभिन्न प्रकार के मौसम आते हैं। अपने अक्ष पर यह 24 घण्टे में एक चक्कर पूरा करती है
जिससे इस पर दिन और रात होती है। चन्द्रमा के पृथ्वी के निकट होने के कारण यह पृथ्वी पर मौसम के लिए दायी है। इसके
आकर्षण के कारण इस पर ज्वार-भाटे उत्पन्न होता है। चन्द्रमा पृथ्वी का एकमात्र प्राकृतिक उपग्रह है।
'''},


{'language': 'Emoji',
 'main_script': 'Common',
 'script_variant': 'Emoji',
 'expected_family_names': ['Noto Color Emoji', 'Apple Color Emoji'] if platform.system() == "Darwin" else 
                          ['Noto Color Emoji', 'Segoe UI Emoji'] if platform.system() == "Windows" else
                          ['Noto Color Emoji'],
 'expected_family_name': 'Apple Color Emoji' if platform.system() == "Darwin" else
                         'Segoe UI Emoji' if platform.system() == "Windows" else
                         'Noto Color Emoji',
 'is_rtl': False,
 'text': # Text below is just some sample emoji
'''
😀😃😄😁🐶🐱🐭🐹🍏🍎🍐🍊⚽️🏀🏈⚾️🚗🚕🚙🚌⌚️📱📲💻🩷❤️🧡💛🏳️🏴🏴‍☠️🏁
'''},
]
