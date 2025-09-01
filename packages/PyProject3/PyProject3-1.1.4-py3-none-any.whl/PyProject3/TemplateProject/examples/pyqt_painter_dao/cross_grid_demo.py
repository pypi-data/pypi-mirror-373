# -*- coding: utf-8 -*-

"""
尺子。
"""
import os
import sys
import math
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (QMainWindow, QWidget, QSlider, QApplication,
                             QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QMenu,
                             QDialog, QFormLayout, QTextEdit, QDialogButtonBox)
from PyQt5.QtCore import QObject, Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QCursor, QImage
import winreg
import wmi
import requests
import datetime
import logging

DATA_ROOT = r'D:\xmov\projects\gitee\technology\articles\matlab\images'

logger = logging.getLogger()

def download(url, local_file=None):
    if local_file is None:
        _, ext = os.path.splitext(url)
        name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        local_file = f'{DATA_ROOT}/{name}{ext}'
    try:
        res = requests.get(url)
        with open(local_file, 'wb') as f:
            f.write(res.content)
        clipboard = QApplication.clipboard()
        clipboard.setText(local_file)
        logger.info(f"image download successed! url:{url}\n local_file: {local_file}")
    except Exception as e:
        print(e)


def get_device():
    PATH = "SYSTEM\\ControlSet001\\Enum\\"
    oWmi = wmi.WMI()
    # 获取屏幕信息
    monitors = oWmi.Win32_DesktopMonitor()
    m = monitors[0]
    subPath = m.PNPDeviceID
    infoPath = PATH + subPath + "\\Device Parameters"
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, infoPath)
    # 屏幕信息按照一定的规则保存（EDID）
    value = winreg.QueryValueEx(key, "EDID")[0]
    winreg.CloseKey(key)
    width, height = value[21], value[22]
    widthResolution = value[56] + (value[58] >> 4) * 256
    heightResolution = value[59] + (value[61] >> 4) * 256
    widthDensity = widthResolution / (width / 2.54)
    heightDensity = heightResolution / (height / 2.54)

    class info(object):
        width_cm = width
        height_cm = height
        width_resolution = widthResolution
        height_resolution = heightResolution
        width_ppi = widthDensity
        height_ppi = heightDensity

    return info


SCREEN_INFO = get_device()  # 屏幕信息

Daos = {'1': '道可道，非常道 名可名，非常名 无名，天地之始 有名，天地之母 故常无，欲以观其妙 常有，欲以观其缴 此两者同出而异名 同谓之玄 玄之又玄 众妙之门',
        '2': '天下皆知美之为美，斯恶矣 皆知善之为善，斯不善矣 故有无相生，难易相成 长短相形，高下相倾 音声相和，前后相随 是以圣人处无为之事 行不言之教 万物做焉而不辞 生而不有，为而不恃 功成而弗居 夫唯弗居，是以不去',
        '3': '不尚贤，使民不争 不贵难得之货，使民不为盗 不见可欲，使民心不乱 是以圣人之治： 虚其心，实其腹 弱其智，强其骨 常使民无知无欲 使夫智者不敢为也 为无为，则无不治',
        '4': '道冲 而用之或不盈渊兮 似万物之宗 挫其锐 解其纷 和其光 同其尘 湛兮似或存 吾不知谁之子 象帝之先',
        '5': '天地不仁 以万物为刍狗 圣人不仁 以百姓为刍狗 天地之间 其犹橐龠乎 虚而不屈 动而欲出 多言数穷 不如守中',
        '6': '谷神不死 是谓玄牝 玄牝之门 是谓天地根 绵绵若存 用之不勤',
        '7': '天长地久 天地所以能长且久者 以其不自生 故能长生 是以圣人后其身而身先 外其身而身存 非以其无私邪？ 故能成其私。',
        '8': '上善若水 水善利万物而不争 处众人之所恶 故几于道 居善地 心善渊 与善人 言善信 政善治 事善能 动善时 夫唯不争 故无尤',
        '9': '持而盈之 不如其已 揣而锐之 不可常保 金玉满堂 莫知能守 富贵而娇 自遗其咎 功遂身退 天之道',
        '10': '载营魄抱一，能无离乎 专气致柔，能婴儿乎 涤除玄览，能无疵乎 爱民治国，能无为乎 天门开阖，能无雌乎 明白四达，能无知乎 生之畜之 生而不有，为而不恃，长而不宰 是谓玄德',
        '11': '三十辐共一毂 当其无，有车之用 埏埴以为器 当其无，有器之用 凿户牖以为室 当其无，有室之用 有之以为利 无之以为用',
        '12': '五色令人目盲 五音令人耳聋 五味令人口爽 驰骋畋猎另人心发狂 难得之货另人行妨 是以圣人为腹不为目 故去彼取此',
        '13': '宠辱若惊，贵大患若身 何谓宠辱若惊 宠为上，辱为下 得之若惊，失之若惊 是谓宠辱若惊 何谓贵大患若身 吾所以有患，为吾有身 及吾无身，吾有何患 故贵以身为天下，若可寄天下 爱以身为天下，若可托天下',
        '14': '视之不见名曰夷 听之不闻名曰希 搏之不得名曰微 此三者不可致颉 故混而为一 其上不缴 其下不昧 绳绳不可名 夫归于无物 是谓无状之状 无象之象 是谓惚恍 恍兮惚兮 其中有象 惚兮恍兮 其中有物 迎之不见其首 随之不见其后 执古之道 以御今之有 能知古始 是谓道纪',
        '15': '古之善为道者，微妙玄通，深不可识。夫唯不可识，故强为之容： 豫兮若冬涉川 犹兮若畏四邻 俨兮其若客 涣兮其若冰释 敦兮其若朴 旷兮其若谷 混兮其若浊 孰能浊以止 静之徐清 孰能安以久 动之徐生 保此道者不欲盈 夫唯不盈 故能蔽而新成',
        '16': '致虚极 守静笃 万物并作 吾以观复 夫物芸芸 各复归其根 归根曰静 是谓复命 复命曰常 知常曰明 不知常 妄作凶 知常容 容乃公 公乃王 王乃天 天乃道 道乃久没身不殆',
        '17': '太上，不知有之 其次，亲而誉之 其次，畏之 其次，侮之 信不足焉，有不信焉 悠兮，其贵言 功遂事遂 百姓皆谓，我自然',
        '18': '大道废，有仁义 智慧出，有大伪 六亲不和，有孝慈 国家混乱，有忠臣',
        '19': '绝圣弃智 民利百倍绝仁弃义 民复孝慈绝巧弃利 盗贼无有此三者以为文不足故令有所属：见素抱朴 少思寡欲 绝学无忧',
        '20': '唯之于阿 相去几何善之于恶 相去若何人之所畏 不可不畏 荒兮其未央哉 众人熙熙 如享太牢 如春登台 我独泊兮其未兆 如婴儿之未孩 众人皆有余 而我独若遗 我愚人之心也哉 沌沌兮 俗人昭昭 我独昏昏 俗人察察 我独闷闷 湛兮其若海 辽兮若无止 众人皆有以 而我独顽似鄙 我独异于人 而贵食母',
        '21': '孔德之容 唯道是从道之为物 唯恍唯惚 惚兮恍兮 其中有象 恍兮惚兮 其中有物 窈兮冥兮 其中有精 其精甚真 其中有信 自古及今 其名不去 以阅众甫吾 何以知众甫之状哉 以此',
        '22': '曲则全 枉则直 洼则盈 蔽则新 少则得 多则惑 是以圣人抱一为天下式 不自见故明 不自是故彰 不自伐故有功 不自矜故长 夫唯不争 故天下莫能与之争 古之所谓曲则全者 其虚言哉 诚全而归之',
        '23': '希言自然 故飘风不终朝 骤雨不终日 孰为此者 天地 天地尚不能久 而况于人乎 故从事于道者同与道 德者同与德 失者同于失 同于道者道亦乐得之 同于德者德亦乐得之 同于失者失亦乐得之 信不足焉 有不信焉',
        '24': '企者不立 跨者不行 自见者不明 自是者不彰 自伐者无功 自矜者不长 其在道也 曰余食赘形 物或恶之 故有道者不处',
        '25': '有物混成 先天地生 寂兮廖兮 独立不改 周行而不殆 可以为天地母 吾不知其名 字之曰道 强为之名曰大 大曰逝 逝曰远 远曰反 故道大 天大 地大 人亦大 域中有四大 而人居其一焉 人法地 地法天 天法道 道法自然',
        '26': '重为轻根 静为燥君 是以圣人终日行不离缁重 虽有荣观 燕处超然 奈何万乘之主 而以身轻天下 轻则失根 躁则失君',
        '27': '善行无辄迹 善言无瑕谪 善数不用筹策 善闭无关楗不可开 善结无绳约不可解 是以圣人常善救人 故无弃人 常善救物 故无弃物 是谓袭明 故善人者 不善人之师 不善人者 善人之资 不贵其师 不爱其资 虽智大迷 是谓要妙',
        '28': '知其雄 守其雌 为天下溪 为天下溪 常德不离 复归于婴儿 知其白 守其黑 为天下式 为天下式 常德不忒 复归于无极 知其荣 守其辱 为天下谷 为天下谷 常德乃足 复归于朴 朴散则为器 圣人用之 则为官长 故大智不割',
        '29': '将欲取天下而为之 吾见其不得已 天下神器不可为也 不可执也为者败之 执者失之 故物或行或随 或吹或嘘 或强或累 或挫或毁 是以圣人去甚、去奢、其泰',
        '30': '以道佐人主者 不以兵强天下 其事好还 师之所处 荆棘生焉 大军之后 必有凶年 善者果而已 不敢以取强 果而勿矜 果而勿伐 果而勿骄 果而不得已 果而勿强 物壮则老 是谓不道 不道早已。',
        '31': '夫兵者不祥之器 物或勿之 故有道者不处 君子居则贵左 用兵则贵右 兵者不祥之器 非君子之器 胜者不美 而美之者 是乐杀人 夫乐杀人者 则不可得志于天下也 吉事尚左 凶事尚右 偏将军居左 上将军居右 言以丧礼处之 杀人之众以哀悲泣之 战胜以丧礼处之',
        '32': '道常无名，朴虽小 天下莫能臣 侯王若能守之 万物将自宾 天地相合，以降甘露 民莫之令而自均 始制有名，名亦既有 夫亦将知止，知止不殆 譬道之在天下 犹川谷之于江海',
        '33': '知人者智，自知者明 胜人者有力，自胜者强 知足者富，强人者有志 不失其所者久 死而不亡者寿',
        '34': '大道泛兮 其可左右 万物恃之而生而不辞 功成不名有 衣养万物而不为主 可名为小 万物归焉而不为主 可名为大 以其终不为大 故能成其大',
        '35': '执大象 天下往 往而不害 安平泰 乐与耳 过客止 道之出口 淡乎其无味 视之不足见 听之不足闻 用之不足既',
        '36': '将欲歙之，必固张之 将欲弱之，必固强之 将欲废之，必固兴之 将欲夺之，必固与之 是谓微明 柔弱胜刚强 鱼不可脱于渊 国之利器不可以示人',
        '37': '道常无为而无不为 侯王若能守之 万物将自化 化而欲作 吾将镇之以无名之朴 镇之以无名之朴 亦将不欲 不欲以静 天下将自定',
        '38': '上德不德，是以有德 下德不失德，是以无德 上德无为而无以为 下德为之而有以为 上仁为之而无以为 上义为之而有以为 上礼为之而莫之应 则攘臂而扔之 故失道而后德 失德而后仁 失仁而后义 失义而后礼 夫礼者 忠信之薄而乱之首 前始者 道之华而愚之始 是以大丈夫处其厚不居其薄 处其实不居其华 故去彼取此',
        '39': '昔之得一者：天得一以清地得一以宁神得一以灵谷得一以盈万物得一以生侯王得一以为天下贞其致之：天无以清将恐裂地无以宁将恐废神无以灵将恐歇谷无以盈将恐竭万物无以生将恐灭侯王无以为贞将恐撅故贵以贱为本 高以下为基是以侯王自称孤、寡、不谷此非以贱为本邪？非乎？故至数誉无誉不欲琭琭如玉 珞珞如石',
        '40': '反者，道之动 弱者，道之用 天下万物生于有 有生于无',
        '41': '上士闻道，勤而行之 中士闻道，若存若亡 下士闻道，大笑之 不笑，不足以为道 故建言有之： 明道若昧 进道若退 夷道若累 上德若谷 大白若辱 广德若不足 建德若偷 质真若渝 大方无隅 大器晚成 大音希声 大象无形 道隐无名 夫唯道，善贷且成',
        '42': '道生一 一生二 二生三 三生万物 万物负阴而抱阳 冲气以为和 人之所恶 孤、寡、不毂 而王公以为称 故物或损之而益 或益之而损 人之所教 我亦教之 强梁者不得其死 吾将以为教父',
        '43': '天下之至柔 驰骋天下之至坚 无有入无间 吾是以知无为之有益 不言之教 无为之益 天下希及之',
        '44': '名与身孰亲 身与货孰多得与亡孰病是以甚爱必大费 多藏必厚亡知足不辱 知之不殆 可以长久',
        '45': '大成若缺 其用不弊大盈若冲 其用不穷大直若屈 大巧若拙 大辩若讷静胜燥 寒胜热清静为天下正',
        '46': '天下有道 却走马以粪 天下无道 戎马生于郊 祸莫大于不知足 咎莫大于欲得 知足之足 常足矣',
        '47': '不出户 知天下不窥有 见天道是以圣人不行而知 不见而名 不为而成',
        '48': '为学日益 为道日损 损之又损 以至于无为 无为而无不为 取天下常以无事 及其有事 不足以取天下',
        '49': '圣人无常心 以百姓心为心善者 吾善之不善者 吾亦善之 德善信者 吾信之不信者 吾亦信之 德信是以圣人在天下歙歙为天下浑其心百姓皆注其耳目 圣人皆孩之',
        '50': '出生入死 生之徒十有三 死之徒十有三 人之生、动之死地亦十有三 夫何故？以其生生之厚 盖闻善摄生者 路行不遇兕虎 入军不被甲兵 兕无所投其角 虎无所用其爪 兵无所容其刃 夫何故？以其无死地',
        '51': '道生之 德蓄之 物形之 势成之是以万物莫不尊道而贵德道之尊 德之贵夫莫之命而常自然故道生之，德蓄之，生之育之，亭之毒之 养之覆之生而不有 为而不恃 长而不宰，是谓玄德',
        '52': '天下有始 以为天下母 既得其母 已知其子 既知其子 复守其母 没身不殆 塞其兑 闭其门 终身不勤 开其兑 济其事 终身不救见小曰明 守柔曰强用其光 复归其明无遗身殃 是以习常',
        '53': '使我介然有知 行于大道 唯施是畏大道甚夷 而民好径朝甚除 田甚芜 苍甚虚服文采 带利剑 厌饮食是谓盗芋非道也哉',
        '54': '善建者不拔 善抱者不脱 子孙以祭祀不辍 修之于身 其德乃真 修之于家 其德乃余 修之于乡 其德乃长 修之于国 其德乃丰 修之于天下 其德乃普 故以身观身 以家观家 以乡观乡 以国观国 以天下观天下 吾何以知天下之然哉？以此',
        '55': '含德之厚，比于赤子 毒虫不蜇 猛兽不据 撅鸟不搏 骨弱筋柔而握固 不知牝牡之合而全作 精之至也 终日号而不嗄 和之至也 知和曰常，知常曰明 益生曰祥，心使气曰强物壮则老 谓之不道 不道早已',
        '56': '知者不言，言者不知 塞其兑，闭其门 挫其锐，解其纷 和其光，同其尘 是谓玄同 故而不可得而亲 不可得而疏 不可得而利 不可得而害 不可得而贵 不可得而贱 故为天下贵',
        '57': '以正治国 以奇用兵 以无事取天下 吾何以知其然哉？ 以此： 天下多忌讳，而民多弥贫 民多利器，国家滋昏 人多伎巧，奇物滋起 法令滋彰，盗贼多有 故圣人曰 我无为而民自化 我好静而民自正 我无事而民自富 我无欲而民自朴',
        '58': '其政闷闷，其民淳淳 其政察察，其民缺缺 祸兮，福之所依 福兮，祸之所伏 孰知其极，其无正 正复为奇，善复为妖 人之迷，其日固久 是以圣人方而不割，廉而不刿，直而不肆，光而不耀',
        '59': '治人事天 莫若啬 夫唯啬，谓之早服 早服是谓重积德 重积德则无不克 无不克则莫知其极 莫知其极可以有国 有国之母可以长久 是谓深根固柢长生久视之道',
        '60': '治大国若烹小鲜 以道莅天下其鬼不神 非其鬼不神其神不伤人 非其神不伤人圣人亦不伤人 夫两不相伤 故德交归焉',
        '61': '大国者下流天下之交 天下之牝牝常以静胜牡，以静为下故大国以下小国 则取小国小国以下大国 则取大国故或下以取 或下而取大国不过欲兼蓄人小国不过欲入事人夫两者各得其欲大者益为下',
        '62': '道者 天下之奥善人之宝 不善人之所保美言可以市尊 美行可以加人人之不善 何弃之有？故立天子，置三公虽拱碧以先驷马不如座进此道古之所以贵此道者何？不曰以求得 有罪以免邪？故为天下贵',
        '63': '为无为 事无事 味无味大小多少 抱怨以德图难于其易 为大于其细天下难事必作于易天下大事必作于细是以圣人终不为大 故能成其大夫轻诺必寡信 多易必多难是以圣人犹难之 故终无难矣',
        '64': '其安易持 其未兆易谋其脆易泮 其微易散为之于未有 治之于未乱合抱之木 生于毫末九层之台 起与垒土千里之行 始于足下为者败之 执者失之是以圣人无为故无败无执故无失民之从事 常于几成而败之慎终如始 则无败事是以圣人欲不欲 不贵难得之货学不学 复众人之所过以辅万物之自然而不敢为',
        '65': '古之善为道者非以明民 将以愚之国之难治 以其多智故以智治国 国之贼不以智治国 国之福知此两者以稽式常知稽式 是谓玄德玄德深矣 远矣 与之反矣然后乃至大顺',
        '66': '江海之所以能为百谷王者以其善下之 故能为百谷王是以欲上民必以言下之欲先民必以身后之是以圣人处上而民不重处前而民不害是以天下乐推而不厌以其不争 故天下莫能与之争',
        '67': '天下皆谓我道大 似不肖夫唯大 故似不肖若肖 久矣其细也夫我有三宝，持而保之：一曰慈，二曰俭 三曰不敢为天下先慈故能勇 俭故能广不敢为天下先故能成器长今舍慈且勇 舍俭且广舍后且先 死矣夫慈 以战则胜 以守则固天将救之 以慈卫之',
        '68': '善为士者不武 善战者不怒善胜敌者不与 善用人者为下是谓不争之德 是为用人之力是谓配天古之极',
        '69': '用兵有言：吾不敢为主而为客不敢进寸而退尺是谓行无行 攘无臂 扔无敌 执无兵祸莫大于轻敌 轻敌几丧吾宝故抗兵相加 哀者胜矣',
        '70': '吾言甚易知 甚易行天下莫能知 莫能行言有宗 事有君夫唯不知 是以不我知知我者希 则我者贵是以圣人披褐怀玉', '71': '知不知 上不知知 病圣人不病 以其病病夫唯病病 是以不病',
        '72': '民不畏威 则大威至无狎其所居 无厌其所生夫唯不厌 是以不厌是以圣人自知不自见自爱不自贵故去彼取此',
        '73': '勇于敢 则杀勇于不敢 则活此两者或利或害天之所恶 孰知其故是以圣人犹难之天之道 不争而善胜 不言而善应不召而自来 繟然而善谋天网恢恢 疏而不失',
        '74': '民不畏死 奈何以死惧之若使民常畏死 而为奇者吾得执而杀之 孰敢？常有司杀者杀 夫代司杀者杀是谓代打匠斫 夫代大匠斫者希有不伤其手矣',
        '75': '民之饥以其上食税之多 是以饥民之难治以其上之有为 是以难治民之轻死以其上求生之厚 是以轻死夫唯无以生为者是贤于贵生',
        '76': '人之生也柔弱 其死也坚强万物草木之生以柔脆 其死也枯槁故坚强者死之徒 柔弱者生之徒是以兵强则灭 木强则折强大处下 柔弱处上',
        '77': '天之道，其犹张弓欤 高者仰之，下者举之 有余者损之，不足者补之 天之道，损有余而补不足 人之道，则不然，损不足而奉有余 孰能有余以奉天下，唯有道者 是以圣人为而不恃，功成而不处 其不欲见贤也',
        '78': '天下莫柔弱于水 而攻坚强者莫之能胜 其无以易之 弱之胜强，柔之胜刚 天下莫不知，莫能行 是以圣人云 受国之垢，是谓社稷主 受国不祥，是谓天下王 正言若反',
        '79': '和大怨 必有余怨 安可以为善？是以圣人执左契而不责于人 有德司契，无德司彻 天道无亲，常与善人',
        '80': '小国寡民 使有什伯之器而不用 使民重死而不远徙 虽有舟隅，无所乘之 虽有甲兵，无所陈之 使人复结绳而用之 甘其食，美其服 安其居，乐其俗 邻国相望，鸡犬之声相闻 民至老死，不相往来',
        '81': '信言不美，美言不信 善者不辩，辩者不善 知者不博，博者不知 圣人不积 既以与人，己愈有 既以与人，已愈多 天之道，利而不害 圣人之道，为而不争'}


class ChapterSelectDialog(QDialog):
    Signal_OneParameter = pyqtSignal(str)  # 自定义一个带参的信号

    def __init__(self, parent=None, content=""):
        super(ChapterSelectDialog, self).__init__(parent)
        self.setWindowTitle('goto chapter')
        # 在布局中添加部件
        layout = QFormLayout(self)
        self.label = QLabel(self)
        self.label.setText('章节：')
        self.edit = QTextEdit()
        self.edit.setPlainText(content)
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        # 使用两个button(ok和cancel)分别连接accept()和reject()槽函数
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.emit_signal)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # self.datetime_emit.dateTimeChanged.connect(self.emit_signal)

    def emit_signal(self):
        s = self.edit.toPlainText()
        self.Signal_OneParameter.emit(s)  # 通过内置信号发送自自定义的信号
        self.close()


class CrossGrid(object):
    def __init__(self, x, y, w, h):
        self.painter = None
        self.alpha = 100
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def set_painter(self, painter):
        self.painter = painter

    @staticmethod
    def draw(painter, x, y, w, h, word='你', color=QColor(125, 0, 0, 100), grid=False):
        painter.setPen(QPen(color, 2))
        painter.drawRect(x, y, w, h)
        painter.setPen(QPen(color, 1))
        if grid:
            painter.drawLine(x, y, x + w, y + h)  # /
            painter.drawLine(x + w, y, x, y + h)  # \
            painter.drawLine(x, y + h / 2, x + w, y + h / 2)  # -
            painter.drawLine(x + w / 2, y, x + w / 2, y + h)  # |

        painter.setPen(QPen(color, 1))
        painter.setFont(QFont('华文楷体', w * 0.6, QFont.Bold))

        metrics = painter.fontMetrics()
        fw = metrics.width(word)
        fh = metrics.height()
        metrics.lineSpacing()
        painter.drawText(x + (w - fw) / 2, y + fh * 5 / 6, word)


class GridWidget(QWidget):
    def __init__(self):
        super(GridWidget, self).__init__()
        self._padding = 2
        self.alpha = 100
        self.color = QColor(125, 0, 0)
        self.space = 50
        self.focus = True
        self.is_drawing = False
        self.with_background = False
        self.grid = False
        self._chapter = None
        self.content = self.get_chapter(self.chapter)
        self.chapterDialog = ChapterSelectDialog(parent=self, content=str(self.chapter))
        self.chapterDialog.Signal_OneParameter.connect(self.set_chapter)
        self.initUI()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)
        self.setAcceptDrops(True)

    def set_chapter(self, chapter_str):
        self.chapter = int(chapter_str)

    @property
    def chapter(self):
        if self._chapter is None:
            try:
                with open('cache.tmp', 'r') as f:
                    self._chapter = int(f.read())
            except:
                self._chapter = 1
        return self._chapter

    @chapter.setter
    def chapter(self, value):
        try:
            with open('cache.tmp', 'w') as f:
                f.write(str(value))
        except Exception as e:
            print(e)
        self._chapter = value

    def get_chapter(self, idx):
        if str(idx) in Daos.keys():
            return f'{idx} {Daos[str(idx)]}'
        else:
            return f'不存在第{idx}章'

    def increase_alpha(self, delta=10):
        self.alpha = self.alpha + delta
        self.alpha = min(255, self.alpha)

    def decrease_alpah(self, delta=10):
        self.alpha = self.alpha - delta
        self.alpha = min(255, self.alpha)

    def initUI(self):
        self.setMinimumSize(300, 300)

    def paintEvent(self, e):
        if not self.is_drawing:
            self.is_drawing = True
            qpainter = QPainter()
            qpainter.begin(self)
            # self.drawGrid(qpainter)
            self.drawCrossGrid(qpainter)
            qpainter.end()
            self.is_drawing = False
        # self.setMouseTracking(True)

    def _break_lines(self, content, word_per_line=7):
        lines = []
        for line in content.split():
            line = line + ' ' * (math.ceil(len(line) / word_per_line) * word_per_line - len(line))
            lines.append(line)
        new_content = ''.join(lines)
        # print(new_content)
        return new_content

    def drawCrossGrid(self, qpainter):
        size = self.size()
        w = size.width()
        h = size.height()

        step = grid_width = grid_height = 50
        # pen = QPen(QColor(125, 0, 0), 2)
        # qpainter.setPen(pen)
        if self.with_background:
            color = QColor(255, 255, 255)
            color.setAlpha(self.alpha)
            qpainter.setBrush(color)
            qpainter.drawRect(-10, -10, w, h)
        idx = 0
        self.content = self.get_chapter(self.chapter)
        content = self._break_lines(self.content, word_per_line=len(range(0, w - step, step)))
        for y in range(0, h - step, step):
            for x in range(0, w - step, step):
                word = content[idx] if idx < len(content) else ' '
                self.color.setAlpha(self.alpha)
                CrossGrid.draw(qpainter, x, y, step, step, word, self.color, grid=self.grid)
                idx = idx + 1
        color = QColor(255, 255, 0) if self.focus else self.color  # 高亮方块
        qpainter.setBrush(color)
        qpainter.drawRect(0, h * 2 / 3, 20, 20)  # 大方块
        qpainter.drawRect(w - 20, h - 20, 20, 20)  # 右下角小方块

    def drawGrid(self, qpainter):
        size = self.size()
        w = size.width()
        h = size.height()
        pen = QPen(self.color, 2,
                   Qt.SolidLine)

        qpainter.setPen(pen)
        qpainter.setBrush(QColor(255, 175, 175, 100))

        for (idx, x) in enumerate(range(0, w, self.space)):
            pen = QPen(self.color, 5 if idx % 5 == 0 else 2, Qt.SolidLine)
            qpainter.setPen(pen)
            qpainter.drawLine(x, 0, x, h)
        for (idx, y) in enumerate(range(0, h, self.space)):
            pen = QPen(self.color, 5 if idx % 5 == 0 else 2, Qt.SolidLine)
            qpainter.setPen(pen)
            qpainter.drawLine(0, y, w, y)

        p = qpainter
        rect = p.viewport()
        im = QImage()
        im.load(r'C:\Users\07jia\Documents\projects\gitee\technology\python\examples\a.png')
        size = im.size()
        size.scale(rect.size(), Qt.KeepAspectRatio)
        print(rect)
        print(size)
        p.setViewport(rect.x(), rect.y(), size.width(), size.height())
        print(im.rect())
        p.setWindow(im.rect())
        p.drawImage(0, 0, im)

    def generateMenu(self, pos):
        menu = QMenu()
        item1 = menu.addAction('red')
        item2 = menu.addAction('black')
        item3 = menu.addAction('white')

        menu.addSeparator()
        item4 = menu.addAction('gird on/off')
        item5 = menu.addAction('goto...')
        item6 = menu.addAction('background on/off')

        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.color = QColor(125, 0, 0)
        if action == item2:
            self.color = QColor(0, 0, 0)
        if action == item3:  # white
            self.color = QColor(255, 255, 255)

        if action == item4:
            self.grid = not self.grid
        if action == item5:
            self.space = 50
            self.chapterDialog.show()
        if action == item6:
            self.with_background = not self.with_background
        self.repaint()

    def dragEnterEvent(self, e):
        mime_data = e.mimeData()
        if mime_data.hasUrls:
            for url in mime_data.urls():
                print('drag enter: ', url.toLocalFile())
            e.accept()
            return
        if mime_data.hasFormat("text/plain"):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        # self.setText(e.mimeData().text())
        mime_data = e.mimeData()

        for url in mime_data.urls():
            remote_url = url.toString()
            if remote_url.startswith('http'):
                download(remote_url)
            print('drop event: ', remote_url, url.toLocalFile())



class ResizeAbleMixin(object):
    def __init__(self):
        super(ResizeAbleMixin, self).__init__()
        self._padding = 20
        self.initDrag()

    def initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False

    def mousePressEvent(self, event):
        # print(event.y)
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True
            event.accept()
        elif (event.button() == Qt.LeftButton) and (event.y() < self.height()):
            # 鼠标左键点击标题栏区域
            self._move_drag = True
            self.move_DragPosition = event.globalPos() - self.pos()
            event.accept()
        else:
            pass

    def mouseMoveEvent(self, QMouseEvent):
        # 判断鼠标位置切换鼠标手势
        print(QMouseEvent.pos())
        if QMouseEvent.pos() in self._corner_rect:
            print("pos in _corner_rect")
            self.setCursor(Qt.SizeFDiagCursor)
        elif QMouseEvent.pos() in self._bottom_rect:
            print("pos in _bottom_rect")
            self.setCursor(Qt.SizeVerCursor)
        elif QMouseEvent.pos() in self._right_rect:
            print("pos in _right_rect")
            self.setCursor(Qt.SizeHorCursor)
        else:
            print("pos in others")
            self.setCursor(Qt.OpenHandCursor)  # ArrowCursor
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        print(Qt.LeftButton)
        print(self._right_drag)
        print(self._bottom_drag)
        print(self._corner_drag)
        print(self._move_drag)
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(QMouseEvent.pos().x(), self.height())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(QMouseEvent.pos().x(), QMouseEvent.pos().y())
            QMouseEvent.accept()
        elif Qt.LeftButton and self._move_drag:
            # 标题栏拖放窗口位置
            print("moving")
            print(self.move_DragPosition)
            print(QMouseEvent.globalPos() - self.move_DragPosition)
            self.move(QMouseEvent.globalPos() - self.move_DragPosition)
            QMouseEvent.accept()
        print("mouse moved")

    def mouseReleaseEvent(self, QMouseEvent):
        self._move_drag = False
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
        self.setCursor(QCursor(Qt.ArrowCursor))
        # print(QMouseEvent.pos())
        # print(self._corner_rect)

    def resizeEvent(self, QResizeEvent):
        # self._TitleLabel.setFixedWidth(self.width())  # 将标题标签始终设为窗口宽度
        # try:
        #     self._CloseButton.move(self.width() - self._CloseButton.width(), 0)
        # except:
        #     pass
        # try:
        #     self._MinimumButton.move(self.width() - (self._CloseButton.width() + 1) * 3 + 1, 0)
        # except:
        #     pass
        # try:
        #     self._MaximumButton.move(self.width() - (self._CloseButton.width() + 1) * 2 + 1, 0)
        # except:
        #     pass

        # 重新调整边界范围以备实现鼠标拖放缩放窗口大小，采用三个列表生成式生成三个列表
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                            for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                             for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                             for y in range(self.height() - self._padding, self.height() + 1)]


class MainWindow(ResizeAbleMixin, QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.kb_content = dict(tracking=False, content='')
        self.initUI()
        self.setMouseTracking(True)

    def initUI(self):
        self.wid = GridWidget()
        hbox = QHBoxLayout()
        hbox.addWidget(self.wid)
        vbox = QVBoxLayout()
        # vbox.addStretch(1)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

        # self.setGeometry(0, 0, SCREEN_INFO.width_resolution, SCREEN_INFO.height_resolution)
        self.setGeometry(0, 0, 660, 1000)
        self.setWindowTitle('Burning widget')
        self.show()

    def keyPressEvent(self, e):
        print(str(e.key()))
        if e.key() in [Qt.Key_Up, Qt.Key_W]:
            self.wid.increase_alpha()
        if e.key() in [Qt.Key_Down, Qt.Key_S]:
            self.wid.decrease_alpah()
        if e.key() in [Qt.Key_Left, Qt.Key_A]:
            self.wid.chapter = self.wid.chapter - 1
        if e.key() in [Qt.Key_Right, Qt.Key_D]:
            self.wid.chapter = self.wid.chapter + 1
        if e.key() in [Qt.Key_G, ]:
            self.kb_content['tracking'] = True
        if e.key() in [Qt.Key_Return, ]:
            print(self.kb_content)
            if self.kb_content['tracking']:
                content = self.kb_content['content']
                try:
                    chapter = int(content)
                    self.wid.chapter = chapter
                except Exception as e:
                    print(e)
                self.kb_content['tracking'] = False
            self.kb_content['content'] = ''

        if e.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5,
                       Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9, Qt.Key_0]:
            if self.kb_content['tracking']:
                content = self.kb_content['content'] + chr(e.key())
                self.kb_content['content'] = content

        self.wid.chapter = min(81, max(self.wid.chapter, 1))
        self.wid.repaint()

    def changeEvent(self, a0: QtCore.QEvent) -> None:
        print(a0.type())
        if a0.type() == QtCore.QEvent.ActivationChange:
            if self.isActiveWindow():
                self.wid.focus = True
            else:
                self.wid.focus = False
        a0.accept()

    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        print(a0.phase())


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
