"""种子数据：精酿啤酒知识库
运行方式：python -m scripts.seed_beer_wiki
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from db.session import get_session_factory
from models.beer_style import BeerStyle
from models.beer_item import BeerItem


STYLES = [
    # (name, name_en, category, description, origin_story, tasting_notes, ibu_min, ibu_max, srm_min, srm_max, abv_min, abv_max, icon, sort_order)
    ("IPA", "India Pale Ale", "艾尔", "以浓郁酒花香和高苦度为特征，是精酿革命的旗帜品类。", "18世纪末，英国为长途海运至印度殖民地在啤酒中加入大量酒花以防腐，意外造就了独特的酒花香型。", "闻香：柑橘、松针、热带水果；入口：苦味明显但干净，麦芽甜作衬；收口：干爽回甘。", 40, 70, 6, 14, 5.5, 7.5, "🍺", 1),
    ("世涛", "Stout", "艾尔", "深黑色酒体，带有烘烤麦芽带来的咖啡、巧克力风味，口感丝滑醇厚。", "源自18世纪伦敦的波特啤酒（Porter），'Stout Porter'意为'浓烈波特'，后来简化为Stout。", "闻香：咖啡、黑巧克力、焦糖；入口：烘烤麦芽香主导，奶油般顺滑；收口：微甜或干爽。", 25, 50, 25, 40, 4.0, 7.0, "🖤", 2),
    ("小麦啤酒", "Wheat Beer / Weissbier", "艾尔", "使用大量小麦麦芽酿造，口感清爽柔和，带有香蕉和丁香风味。", "德国巴伐利亚的传统风格，最早可追溯至16世纪，曾是贵族专享的酿造特权。", "闻香：香蕉、丁香的酵母特征香气；口感：气泡感强，酒体浑浊；极其易饮。", 8, 15, 2, 6, 4.3, 5.6, "🌾", 3),
    ("酸啤", "Sour Beer", "艾尔", "故意引入野生酵母或细菌酿造，带来令人愉悦的酸味体验。", "比利时的兰比克（Lambic）是最古老的酸啤传统，利用空气中的野生酵母自然发酵。", "酸味主导，从清新的柠檬酸到复杂的果酸；常加入水果增味；气泡感强，极开胃。", 5, 20, 3, 10, 3.0, 7.0, "🍋", 4),
    ("皮尔森", "Pilsner", "拉格", "世界上消费量最大的啤酒风格，金黄色酒体，干净爽口，苦味适中。", "1842年诞生于捷克皮尔森市，世界第一款金黄色啤酒，从此改变了啤酒的样貌。", "闻香：清淡麦香、微微花香；入口：清脆干净的麦芽味，苦味适中平衡；收口：极为干爽。", 30, 45, 3, 6, 4.2, 5.8, "🍻", 5),
    ("深色拉格", "Dark Lager", "拉格", "拉格家族中的深色系，兼具拉格清爽与烘烤麦芽的焦香。", "慕尼黑邓克尔（Munich Dunkel）是德国最古老的传统啤酒风格之一。", "闻香：焦糖、烤面包、坚果；口感：麦芽甜感突出，酒体中等；收口柔和。", 18, 28, 14, 28, 4.5, 5.6, "🏾", 6),
    ("赛松", "Saison", "特色", "比利时农舍艾尔，曾是农场工人的'解渴口粮'，充满酵母带来的复杂果香和辛香。", "比利时瓦隆地区的农舍夏天酿造、储存，供田间劳作工人饮用。", "闻香：胡椒、柑橘、草本、果香；入口：极干的收口，高碳酸；复杂多变。", 20, 35, 5, 14, 5.0, 7.0, "🌿", 7),
    ("修道院啤酒", "Trappist / Abbey Ale", "特色", "由修道院僧侣酿造或监督的高品质啤酒，风味深邃复杂。", "Trappist标志受法律保护，全世界仅十余家修道院有此资格。", "闻香：深色水果、焦糖、辛香；入口：酒体饱满，复杂的果脯和巧克力味；酒精度偏高。", 20, 35, 15, 25, 6.0, 10.0, "⛪", 8),
    ("果味啤酒", "Fruit Beer", "特色", "在基酒中加入水果或果汁，清新易饮，适合啤酒入门。", "比利时林德曼（Lindemans）等酒厂将水果兰比克发扬光大。", "水果风味为主导，甜酸平衡；气泡感强，颜色鲜艳；极低的苦味。", 5, 15, 3, 20, 2.5, 5.0, "🍒", 9),
    ("烈性艾尔", "Strong Ale / Barleywine", "艾尔", "超高酒精度、饱满酒体，适合小口慢酌的'压轴酒'。", "大麦酒（Barleywine）源自18世纪英国贵族，因酒精度堪比葡萄酒而得名。", "闻香：焦糖、太妃糖、深色水果；入口：麦芽甜感浓郁厚重；收口温热感明显。", 35, 70, 8, 22, 8.0, 12.0, "🔥", 10),
]


BEERS = [
    # (name, name_en, brewery, country, style_name, description, abv, ibu, og, image_url, flavor_tags, is_classic)
    # ── IPA 经典 ──
    ("酿酒狗 朋克IPA", "BrewDog Punk IPA", "酿酒狗 BrewDog", "英国", "IPA", "苏格兰酿酒狗的旗舰酒款，以新世界酒花的多层次果香引爆味蕾，全球精酿入门标杆。", 5.6, 45, 13.5, None, "柑橘,荔枝,松针,热带水果", 1),
    ("岬角 杜父鱼IPA", "Ballast Point Sculpin IPA", "岬角 Ballast Point", "美国", "IPA", "圣地亚哥的传奇IPA，以爆炸性的热带果香闻名，被众多酒友称为IPA教科书。", 7.0, 70, 16.1, None, "芒果,桃子,葡萄柚,蜂蜜", 1),
    ("迷失海岸 迷雾快艇 双倍IPA", "Lost Coast Indica IPA", "迷失海岸 Lost Coast", "美国", "IPA", "加州尤里卡的经典之作，口感顺滑平衡，酒花香气深沉持久。", 6.5, 50, 15.0, None, "松针,柑橘,泥土,焦糖", 1),
    ("深粉象 三料IPA", "Delirium Tremens", "海特安 Huyghe", "比利时", "IPA", "比利时粉象系列的顶级IPA，浓烈但异常平衡，带有比利时酵母特有的果香。", 8.5, 26, 19.0, None, "梨,苹果,辛香,酒精感", 0),
    ("罗格 美人鱼IPA", "Rogue Mermaid IPA", "罗格 Rogue", "美国", "IPA", "俄勒冈的自酿先驱，选用当地特有酒花和海水酿造，微咸鲜甜。", 5.8, 55, 13.5, None, "葡萄柚,松针,微微海盐", 0),

    # ── 世涛经典 ──
    ("左手 牛奶世涛", "Left Hand Milk Stout", "左手 Left Hand", "美国", "世涛", "科罗拉多的标杆牛奶世涛，添加乳糖带来不可发酵的甜感，口感如丝般顺滑。", 6.0, 25, 14.5, None, "咖啡,巧克力,奶油,焦糖", 1),
    ("北岸 老拉斯普京 帝国世涛", "North Coast Old Rasputin", "北岸 North Coast", "美国", "世涛", "以俄国妖僧命名的帝国世涛，浓郁厚重到极致，陈年潜力惊人。", 9.0, 75, 22.0, None, "黑巧克力,深烘咖啡,焦香面包,葡萄干", 1),
    ("健力士 世涛", "Guinness Draught", "健力士 Guinness", "爱尔兰", "世涛", "全世界最著名的世涛，氮气技术带来如奶油般的泡沫和丝滑口感。", 4.2, 45, 9.9, None, "烘烤大麦,咖啡,微苦回甘", 0),
    ("打倒 肯塔基 帝国世涛", "Founders Kentucky Breakfast Stout", "创始者 Founders", "美国", "世涛", "过波本桶酿造的帝国世涛，咖啡与巧克力层叠交织，酒友趋之若鹜。", 12.0, 70, 27.0, None, "波本桶,香草,咖啡豆,黑巧克力,橡木", 1),

    # ── 小麦啤酒 ──
    ("施纳德 经典小麦", "Schneider Weisse Original", "施纳德 Schneider", "德国", "小麦啤酒", "巴伐利亚最古老的小麦啤酒厂，严格遵循传统工艺，香蕉丁香风味典范。", 5.4, 12, 12.5, None, "香蕉,丁香,面包,微酸", 1),
    ("鹅岛 312城市小麦", "Goose Island 312 Urban Wheat", "鹅岛 Goose Island", "美国", "小麦啤酒", "芝加哥的清爽小麦艾尔，适合所有场合的易饮选择。", 4.2, 18, 10.0, None, "柑橘,柠檬,麦香,清爽", 0),
    ("碧特博格 小麦", "Bitburger Weizen", "碧特博格 Bitburger", "德国", "小麦啤酒", "德国经典小麦，清爽柔和，香蕉酯香恰到好处。", 5.0, 12, 11.5, None, "香蕉,麦香,微甜,清爽", 0),

    # ── 酸啤 ──
    ("林德曼 樱桃兰比克", "Lindemans Kriek", "林德曼 Lindemans", "比利时", "酸啤", "比利时樱桃兰比克的巅峰之作，真实樱桃汁发酵，像喝果汁般畅快。", 3.5, 10, 13.0, None, "樱桃,覆盆子,酸甜,气泡", 1),
    ("勃艮第女公爵 佛兰德斯红艾尔", "Duchesse de Bourgogne", "凡登维恩 Verhaeghe", "比利时", "酸啤", "比利时佛兰德斯红艾尔的典范，过橡木桶陈酿带来复杂酸甜韵味。", 6.2, 12, 14.0, None, "红酒醋,橡木,樱桃,甜麦芽", 1),

    # ── 皮尔森 ──
    ("比尔斯奈尔 皮尔森", "Pilsner Urquell", "比尔斯奈尔", "捷克", "皮尔森", "全世界第一款皮尔森，1842年酿造至今，定义了金啤的标准。", 4.4, 40, 11.0, None, "麦芽,花香,苦味清爽,干爽收口", 1),

    # ── 赛松 ──
    ("杜邦 赛松", "Saison Dupont", "杜邦 Dupont", "比利时", "赛松", "赛松风格的绝对标杆，农舍发酵的复杂风味无人能及。", 6.5, 30, 14.0, None, "胡椒,柑橘,泥土,草本,极干", 1),

    # ── 修道院 ──
    ("罗斯福 10号", "Rochefort 10", "罗斯福 Rochefort", "比利时", "修道院啤酒", "被全球酒友奉为'四料之王'，深色果脯和巧克力风味层层递进。", 11.3, 27, 24.0, None, "葡萄干,无花果,黑巧克力,焦糖,辛香", 1),
    ("智美 蓝帽", "Chimay Grande Réserve (Blue)", "智美 Chimay", "比利时", "修道院啤酒", "智美最高等级作品，深琥珀色酒体，复杂度随陈年不断演化。", 9.0, 25, 20.0, None, "焦糖,深色水果,辛香,微苦", 1),
    ("西弗莱特伦 12号", "Westvleteren 12", "西弗莱特伦 Westvleteren", "比利时", "修道院啤酒", "常年霸榜世界第一啤酒，僧侣手工酿造极少量，极度稀有。", 10.2, 38, 20.0, None, "焦糖,黑巧克力,葡萄干,面包,辛香", 1),
]


def seed():
    SessionLocal = get_session_factory()
    with SessionLocal() as session:
        # ── 插入风格品类 ──
        existing_styles = {s.name: s for s in session.query(BeerStyle).all()}
        for s in STYLES:
            if s[0] not in existing_styles:
                style = BeerStyle(
                    name=s[0], name_en=s[1], category=s[2], description=s[3],
                    origin_story=s[4], tasting_notes=s[5], ibu_min=s[6], ibu_max=s[7],
                    srm_min=s[8], srm_max=s[9], abv_min=s[10], abv_max=s[11],
                    icon=s[12], sort_order=s[13],
                )
                session.add(style)
        session.flush()

        # ── 建立风格名称→ID 映射 ──
        style_map: dict[str, int] = {}
        for s in session.query(BeerStyle).all():
            style_map[s.name] = s.id

        # ── 插入酒款 ──
        existing_beers = {b.name: b for b in session.query(BeerItem).all()}
        for b in BEERS:
            if b[0] not in existing_beers:
                style_id = style_map.get(b[4])
                item = BeerItem(
                    name=b[0], name_en=b[1], brewery=b[2], country=b[3],
                    style_id=style_id, description=b[5], abv=b[6], ibu=b[7],
                    og=b[8], image_url=b[9], flavor_tags=b[10], is_classic=b[11],
                )
                session.add(item)

        session.commit()
        print("✅ 精酿知识种子数据插入完成！")


if __name__ == "__main__":
    seed()
