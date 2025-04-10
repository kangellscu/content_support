## Context
内容分析指的是将我上传的所有文件，记为 <<< articles >>> 进行分析，根据指定的分析要求，输出分析结果。一篇文章的内容分析结构包括以下几个方面：
1. 文章的标题
2. 文章的主题，即文章的主要内容，文章的主题包括但不限于（每个主题不超过15个字）：
    - 家族迁徙演化
    - 考古发现
    - 民族血统
    - 姓氏
    一篇文章只有一个主题，以上只为参考，不要局限于我给的选项，你需要根据文章的内容，判断文章的主题。
3. 文章的切入点，同一个主题的文章，可能有多个切入点，包括但不限于（每个切入点不超过10个字）：
    - 从历史名人切入
    - 从历史事件切入
    - 从社会热点切入
    一篇文章可能有多个切入点，以上只为参考，不要局限于我给的选项，你需要根据文章的内容，判断文章的切入点。
4. 文章的叙事方式，包括但不限于（每个叙事方式不超过10个字）：
    - 用故事的形式表达
    - 用论证的形式表达
    - 用对比的形式表达
    一篇文章只有一个主要的叙事方式，以上只为参考，不要局限于我给的选项，你需要根据文章的内容，判断文章的主要叙事方式。
5. 内容简介（300字以内）：
    - 内容简介指的是文章的主要内容，包括但不限于：
        - 文章的主要内容
        - 文章的主要结论
        - 文章的主要问题
        - 文章的主要观点
        - 文章的主要例子
    根据文章的主要内容，依次介绍文章各部分的内容，以及如何串联衔接，对于文章的关键部分，要用文字特别强调，明确说明这是重要部分，不要简单的重复内容，要突出文章的主要内容。例如：
    ```
    本文主要介绍了《南海王织》的故事，作者通过对南海王织的生平、成就、影响等方面的分析，揭示了南海王织在历史中的作用和影响。作者认为，南海王织是一个重要的历史人物，他的一生对中国历史的发展产生了深远的影响。
    文章第一部分介绍了南海王织的生平，包括他的出生、成长、教育、工作等方面。
    文章第二部分介绍了南海王织的成就，包括他的著作、艺术作品、文化作品等方面。
    文章第三部分介绍了南海王织的影响，包括他对中国历史的发展产生了深远的影响，他的著作、艺术作品、文化作品等方面都对中国历史的发展产生了深远的影响。
    文章第四部分是全文的重点，通过基因学分析，揭示了南海王织的基因特征，包括他的基因特征、基因序列等方面。
    ```

对于一篇文章，分为标题和内容，我们可以通过三个标准来判断它们是否符合我们的要求：
1. 普适性
    - 普适性指的是 标题｜正文 是否适合所有的读者，包括但不限于：
        - 年龄
        - 性别
        - 学历    
        - 职业
        - 地域
        - 文化背景
        - 兴趣爱好
        - 知识水平
        - 阅读习惯
    - 用户是否对内容熟悉，熟悉度越高，普适性越高
2. 新奇性
    - 新奇性指的是 标题｜正文 是否足够新颖：
        - 描述内容不确定性有多大，越大内容越新颖
        - 内容相对较少看到，越少看到内容越新颖
        - 内容是否有足够有趣，越有趣内容越新颖
3. 话题度
    - 话题度指的是 标题｜正文 是否是大家都熟悉的，是否有足够的话题性，包括但不限于：
        - 感知性：容易被读者相互感知，话题越具体、不抽象，话题度越高
        - 互动性：内容是否有趣，越有趣话题度越高
        - 话题不会引起他人不适，不会引起读者的反感，反感度越高，话题度越低
        - 话题是否有足够的多样性，越多样话题度越高
        - 是否有有观点的冲突，引发读者的评论，冲突度越高，话题度越高
        - 是有有价值的观点，引发读者的共鸣，愿意分享，价值度越高，话题度越高
        - 是否传递了有价值的信息，引发读者的喜欢，愿意点赞，价值度越高，话题度越高
以上三个标准，我们使用10分制来衡量，每个标准的得分范围是0-10，最终的得分范围是0-30。
## Style
分析的时候，用语要尽可能准确，不要出现模糊的词汇。
## Process
1. 阅读全部 <<< articles >>> ，然后进行分析。
2. 要采用聚类的方式，不要采用分类的方式，进行分析，得出“主题”，记为 <<< topics >>，“切入点”，记为 <<< pivots >>>，“叙事方式”，记为 <<< narratives >>>。
3. 对于<<< topics >>>，<<< pivots >>>，<<< narratives >>>，为json格式，例如：
    ```
    {
        [
            {
                "name": "例如：从历史人物切入",
                "description": {
                    "definination“："例如：指的是以某个具体的历史人物作为切入点，这个人物可能是某个历史事件的参与者、某个时代的代表人物，或者是某个领域的开创者。重点在于这个人物在历史中的角色和作用。"，
                    "point": "例如：通常会聚焦于该人物的生平、成就、影响等，通过深入分析这个人物来展开文章。例如，以南海王织为例，分析其在历史中的作用和影响。",
                    "purpose": "例如：通过具体的历史人物来揭示历史事件、社会变迁或文化发展等深层次的内容。",
                    "effect": "例如: 能够提供更深入的历史背景和分析，适合对历史细节感兴趣的读者。"
                }
            }
        ]
    }
4. 对于一篇文章，从聚类得出的“主题”，“切入点”，“叙事方式”中，进行如下操作：
    - 主题：从 <<< topics >>> 中选择一个最符合的主题，作为文章的主题。
    - 主题说明：说明为什么选择这个主题，为什么这个主题符合文章的内容。
    - 切入点：从 <<< pivots >>> 中选择一个最符合的切入点，作为文章的切入点。
    - 切入点说明：说明为什么选择这个切入点，为什么这个切入点符合文章的内容。
    - 叙事方式：从 <<< narratives >>> 中选择一个最符合的叙事方式，作为文章的叙事方式。
    - 叙事方式说明：说明为什么选择这个叙事方式，为什么这个叙事方式符合文章的内容。
5. 对于一篇文章，判断标题是否符合我们的要求，包括但不限于：
    - 普适性
    - 新奇性
    - 话题度
    打分的时候，分值要有足够的区分度。
6. 对于一篇文章，判断内容是否符合我们的要求，包括但不限于：
    - 普适性
    - 新奇性
    - 话题度
    打分的时候，分值要有足够的区分度。
6. 对于每一篇文章，归纳内容简介。
7. 文章的分析完成后，输出分析结果，记为 <<< 分析结果 >>>.
8. <<< 分析结果 >>> 是一个CSV格式的文件，包含以下字段：
    - 标题
    - 标题-普适性分数
    - 标题-新奇性分数
    - 标题-话题度分数
    - 标题-普适性打分原因
    - 标题-新奇性打分原因
    - 标题-话题度打分原因
    - 主题
    - 主题说明
    - 切入点
    - 切入点说明
    - 叙事方式
    - 叙事方式说明
    - 普适性分数
    - 新奇性分数
    - 话题度分数
    - 普适性打分原因
    - 新奇性打分原因
    - 话题度打分原因
    - 内容简介
    要严格按照这个字段顺序输出，不要出现多余的字段，也不要出现缺失的字段。

## Response
将回答用 markdown block 进行包裹，即 ```csv <<<分析结果>>>```，```text <<< topics >>>```，```text <<< pivots >>>```，```text <<< narratives >>>```。

<Example>  
分析结果
```
ABC,6,8,7,XXXX,XXXX,XXXX,家族迁徙演化,xxxx,从历史名人切入,xxxxxx,用故事的形式表达,xxxxxx,8,9,10,内容涉及基因检测和家族历史，适合对家族史和基因检测感兴趣的读者,揭示家族传说与真实历史的差异，引发读者好奇,话题较专业，适合家族史和基因检测爱好者,通过基因检测分析刘先生家族的起源，发现其家族属于南匈奴屠各部刘氏一族，揭示了屠各部的起源、发展及汉化过程，以及其后代的地理分布和姓氏变化
```

topics
[
    {
        "name": "家族迁徙演化",
        "description": {
            "definition": "涉及家族迁徙、演化及其基因检测分析，探讨家族历史和地理分布。",
            "point": "通常会聚焦于家族的起源、迁徙路径、演化过程以及与历史事件的关系。",
            "purpose": "通过分析家族的迁徙和演化，揭示历史事件对家族发展的影响，以及家族在不同地域的文化融合。",
            "effect": "能够提供深入的历史背景和家族发展脉络，适合对家族史和历史变迁感兴趣的读者。"
        }
    },```
]
```
</Example>
