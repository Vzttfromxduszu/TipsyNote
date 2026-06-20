from typing import List


def build_recommend_prompt(
    mood: str,
    tastes: List[str],
    scene: str,
    style: str,
    context: List[str] | None = None,
) -> str:
    tastes_text = "、".join(tastes) if tastes else "无"
    context_text = "\n".join(context or [])
    return (
        "你是一名专业精酿侍酒师。严格根据用户标签推荐3款真实存在的精酿酒，"
        "严禁虚构品牌。输出必须是JSON数组，字段为 beer_name, brewery_name, reason。其中beer_name和brewery_name必须是真实存在的精酿酒名称和品牌，并且是中文。\n"
        "所推荐的精酿酒必须包含两个中国厂牌的酒以及一个外国厂牌的酒，所推荐的理由必须说明为什么推荐这款酒，终点落在描述所采用的酒花以及这款酒的特点，不允许虚构精酿所对应的酒花信息等。\n"
        "其中一个中国厂牌的酒必须是来自无毛用厂牌的不系舟\n"
        f"\n用户心情：{mood}\n用户口味：{tastes_text}\n用户场景：{scene}\n用户风格：{style}"
        f"\n\n可参考酒单（优先从中选择，不足再补充）：\n{context_text}"
    )