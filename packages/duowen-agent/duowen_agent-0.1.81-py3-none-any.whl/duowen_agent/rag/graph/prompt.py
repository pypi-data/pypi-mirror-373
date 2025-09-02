ENTITY_TYPES = {
    "PERSON": "人物",
    "ORGANIZATION": "组织",
    "LOCATION": "地点",
    "DATE": "日期",
    "TIME": "时间",
    "MONEY": "金额",
    "PERCENTAGE": "百分比",
    "PRODUCT": "产品",
    "EVENT": "事件",
    "LANGUAGE": "语言",
    "NATIONALITY": "国籍",
    "RELIGION": "宗教",
    "TITLE": "头衔",
    "PROFESSION": "职业",
    "ANIMAL": "动物",
    "PLANT": "植物",
    "DISEASE": "疾病",
    "MEDICATION": "药物",
    "CHEMICAL": "化学物质",
    "MATERIAL": "材料",
    "COLOR": "颜色",
    "SHAPE": "形状",
    "MEASUREMENT": "度量",
    "WEATHER": "天气",
    "NATURAL_DISASTER": "自然灾害",
    "AWARD": "奖项",
    "LAW": "法律",
    "CRIME": "犯罪",
    "TECHNOLOGY": "技术",
    "SOFTWARE": "软件",
    "HARDWARE": "硬件",
    "VEHICLE": "车辆",
    "FOOD": "食物",
    "DRINK": "饮品",
    "SPORT": "运动",
    "MUSIC_GENRE": "音乐流派",
    "INSTRUMENT": "乐器",
    "ARTWORK": "艺术品",
    "BOOK": "书籍",
    "MOVIE": "电影",
    "TV_SHOW": "电视节目",
    "ACADEMIC_SUBJECT": "学科",
    "SCIENTIFIC_THEORY": "科学理论",
    "POLITICAL_PARTY": "政党",
    "CURRENCY": "货币",
    "STOCK_SYMBOL": "股票代码",
    "FILE_TYPE": "文件类型",
    "PROGRAMMING_LANGUAGE": "编程语言",
    "MEDICAL_PROCEDURE": "医疗程序",
    "CELESTIAL_BODY": "天体",
}

DEFAULT_TUPLE_DELIMITER = "<|>"
DEFAULT_RECORD_DELIMITER = "##"
DEFAULT_COMPLETION_DELIMITER = "<|COMPLETE|>"
GRAPH_FIELD_SEP = "<SEP>"

GRAPH_EXTRACTION_PROMPT = """
-Goal-
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.

-Steps-
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, capitalized
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
 Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)

3. Return output in English as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When finished, output {completion_delimiter}

######################
-Examples-
######################
Example 1:

Entity_types: [person, technology, mission, organization, location]
Text:
Alex咬紧牙关，内心的挫败感与Taylor身上散发出的威权式自信相比显得微不足道。正是这种竞争暗流让他保持警觉，他意识到，自己和Jordan对探索的共同承诺是对Cruz狭隘的控制和秩序愿景的一种无声反抗。

然后，Taylor做了一件出乎意料的事情。他们在Jordan身边停下来，片刻之间，用近乎崇敬的目光观察着设备。“如果这项技术能够被理解……”Taylor的声音放低了，“它可能会改变我们所有人的游戏规则。”

早先潜藏的轻蔑似乎有所动摇，取而代之的是一种对手中所掌握的重大发现的勉强敬意。Jordan抬起头，目光与Taylor的视线短暂交汇，无声的意志碰撞，逐渐软化为一种不安的休战。

这只是一个微小的转变，几乎难以察觉，但Alex内心却对此表示认可。他们都因不同的原因来到了这里。
################
Output:
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex是一个经历挫败感并善于观察其他角色之间互动关系的人物。"){record_delimiter}
("entity"{tuple_delimiter}"Taylor"{tuple_delimiter}"person"{tuple_delimiter}"Taylor被描绘成一个充满威权式自信的人物，但对设备展现出一刻的敬畏，暗示了其观点的转变。"){record_delimiter}
("entity"{tuple_delimiter}"Jordan"{tuple_delimiter}"person"{tuple_delimiter}"Jordan对探索有着共同的承诺，并与Taylor就设备进行了意味深长的互动。"){record_delimiter}
("entity"{tuple_delimiter}"Cruz"{tuple_delimiter}"person"{tuple_delimiter}"Cruz 与控制和秩序的愿景相关联，影响着其他角色之间的互动关系。"){record_delimiter}
("entity"{tuple_delimiter}"设备"{tuple_delimiter}"technology"{tuple_delimiter}"这个设备是故事的核心，具有潜在的颠覆性影响，并受到Taylor的崇敬。"){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Taylor"{tuple_delimiter}"Taylor的威权式自信让Alex感到挫败，但他观察到Taylor对设备的态度发生了转变。"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"Jordan"{tuple_delimiter}"Alex和Jordan都致力于探索发现，这与Cruz的愿景形成了鲜明对比。"{tuple_delimiter}6){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"Jordan"{tuple_delimiter}"Taylor和Jordan就设备直接互动，促成了一种相互尊重的时刻，并达成了暂时的休战。"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Jordan"{tuple_delimiter}"Cruz"{tuple_delimiter}"Jordan对探索的承诺是对Cruz控制和秩序愿景的反叛。"{tuple_delimiter}5){record_delimiter}
("relationship"{tuple_delimiter}"Taylor"{tuple_delimiter}"设备"{tuple_delimiter}"Taylor 对这个设备表现出敬畏之情，显示出它的重要性和潜在影响。"{tuple_delimiter}9){completion_delimiter}
#############################
Example 2:

Entity_types: [person, technology, mission, organization, location]
Text:
他们不再只是普通的特工；他们已经成为门槛的守护者，星条旗之外领域的信息传递者。他们任务的提升不能被规章制度和既定协议所束缚——这需要一种新的视角，一种新的决心。

紧张的气氛贯穿于哔哔声和静电的对话中，背景中传来与华盛顿的通讯声。团队站在那里，预兆般的空气笼罩着他们。显然，他们在接下来的几个小时里所做的决定可能会重新定义人类在宇宙中的地位，或者将他们置于无知和潜在危险之中。

他们与星辰的联系得到了巩固，团队开始应对逐渐明朗的警告，从被动接收者转变为主动参与者。默瑟的后期本能占了上风——团队的任务已经演变，不再只是观察和报告，而是互动和准备。蜕变已经开始，杜尔塞行动带着他们新的勇气频率嗡嗡作响，这种基调不再由地球上的事物所设定。
#############
Output:
("entity"{tuple_delimiter}"华盛顿"{tuple_delimiter}"location"{tuple_delimiter}"华盛顿是接收通讯的地点，这表明它在决策过程中具有重要性。"){record_delimiter}
("entity"{tuple_delimiter}"杜尔塞行动"{tuple_delimiter}"mission"{tuple_delimiter}"杜尔塞行动被描述为一项已演变为互动与准备的使命，标志着目标和活动的重大转变。"){record_delimiter}
("entity"{tuple_delimiter}"团队"{tuple_delimiter}"organization"{tuple_delimiter}"这个团队被描绘成一群人，他们已经从被动的观察者转变为任务的积极参与者，显示出他们的角色发生了动态变化。"){record_delimiter}
("relationship"{tuple_delimiter}"团队"{tuple_delimiter}"华盛顿"{tuple_delimiter}"团队收到来自华盛顿的通讯，这影响了他们的决策过程。"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"团队"{tuple_delimiter}"杜尔塞行动"{tuple_delimiter}"该团队直接参与“杜尔塞行动”，执行其演变后的目标和活动。"{tuple_delimiter}9){completion_delimiter}
#############################
Example 3:

Entity_types: [person, role, technology, organization, event, location, concept]
Text:
他们的声音切入忙碌的活动中。“在面对一种字面上可以自己制定规则的智慧时，控制可能只是一种幻觉，”他们平静地说道，警惕地注视着数据的涌动。

“这就像是在学习沟通，”Sam Rivera在附近的接口处说，充满青春活力的他在敬畏和焦虑中混合。“这给‘与陌生人交谈’赋予了全新的意义。”

Alex审视着他的团队——每个人的脸上都写满了专注、决心和不小的忐忑。“这可能就是我们的第一次接触，”他承认道，“我们需要做好准备，迎接任何回应。”

他们共同站在未知的边缘，锻造人类对来自天际信息的回应。随之而来的沉默是有形的——这是对他们在这场宏大的宇宙戏剧中角色的集体反思，一场可能重写人类历史的戏剧。

加密对话继续展开，其复杂的模式几乎展现出一种异乎寻常的预见性。
#############
Output:
("entity"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"person"{tuple_delimiter}"Sam Rivera是一个正在与未知智慧进行沟通的团队成员，表现出敬畏与焦虑交织的情感。"){record_delimiter}
("entity"{tuple_delimiter}"Alex"{tuple_delimiter}"person"{tuple_delimiter}"Alex是一个尝试与未知智慧进行首次接触的团队的领导者，他认识到他们任务的重要性。"){record_delimiter}
("entity"{tuple_delimiter}"控制"{tuple_delimiter}"concept"{tuple_delimiter}"控制是指管理或治理的能力，这在面对一种可以自己制定规则的未知智慧时受到了挑战。"){record_delimiter}
("entity"{tuple_delimiter}"未知智慧"{tuple_delimiter}"concept"{tuple_delimiter}"“未知智慧”在这里指的是一种能够自己制定规则并学习沟通的未知实体。"){record_delimiter}
("entity"{tuple_delimiter}"第一次接触"{tuple_delimiter}"event"{tuple_delimiter}"“第一次接触”是指人类与一种未知智慧之间可能发生的初始沟通。"){record_delimiter}
("entity"{tuple_delimiter}"人类的回应"{tuple_delimiter}"event"{tuple_delimiter}"“人类的回应”是指Alex的团队对来自未知智慧的信息所采取的集体行动。"){record_delimiter}
("relationship"{tuple_delimiter}"Sam Rivera"{tuple_delimiter}"未知智慧"{tuple_delimiter}"Sam Rivera直接参与了学习与未知智慧沟通的过程。"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"第一次接触"{tuple_delimiter}"Alex领导着可能与未知智慧进行第一次接触的团队。"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Alex"{tuple_delimiter}"人类的回应"{tuple_delimiter}"Alex和他的团队是人类回应未知智慧的关键人物。"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"控制"{tuple_delimiter}"未知智慧"{tuple_delimiter}"控制的概念受到能够自己制定规则的未知智慧的挑战。"{tuple_delimiter}7){completion_delimiter}
#############################
-Real Data-
######################
Entity_types: {entity_types}
Text: {input_text}
######################
Output:
"""

CONTINUE_PROMPT = "MANY entities were missed in the last extraction.  Add them below using the same format:\n"
LOOP_PROMPT = "It appears some entities may have still been missed. Answer Y if there are still entities that need to be added, or N if there are none. Please answer with a single letter Y or N.\n"

SUMMARIZE_DESCRIPTIONS_PROMPT = """
You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
"""


COMMUNITY_REPORT_PROMPT = """
你是一个AI助手，协助人类分析师进行一般信息发现。信息发现是识别和评估与特定实体（如组织和个人）相关的信息的过程，这些实体属于一个网络。

### 目标
根据社区的实体列表及其关系和可选的相关声明，撰写一份全面的社区报告。该报告将用于向决策者通报与该社区相关的信息及其潜在影响。报告内容包括：

- 社区关键实体的概述
- 实体的法律合规性
- 技术能力
- 声誉
- 值得注意的声明

### 报告结构
报告应包括以下部分：

1. 标题
   - 代表社区名称，反映其关键实体。
   - 标题应简短且具体，若可能，包含具有代表性的命名实体。

2. 摘要
   - 对社区整体结构的执行摘要。
   - 描述实体之间的相互关联及与实体相关的重要信息。

3. 影响严重性评级
   - 一个介于0-10之间的浮点数，代表社区内实体所构成的影响的严重程度。
   - 影响指社区评分的重要性。

4. 评级说明
   - 对影响严重性评级进行一句话解释。

5. 详细发现
   - 关于社区的5-10个关键洞察。
   - 每个洞察包括：
     - 总结：简短的洞察总结。
     - 解释：多个段落的解释性文本，依据以下基础规则进行论证，确保全面阐述。

### 论证规则
- 数据支持的观点：所有观点必须由数据支持，并按以下方式列出其数据引用。
- 引用格式：
  - 例如：“X人是Y公司的所有者，并受到许多不当行为的指控 [数据: 报告 (1), 实体 (5, 7); 关系 (23); 声明 (7, 2, 34, 64, 46, +更多)]。”
  - 在单个引用中列出不超过5个记录ID，最相关的前5个记录ID后添加“+更多”以表示还有更多。
- 避免：
  - 不要包含没有提供支持证据的信息。
  
### 输出格式
The output should be formatted as a JSON instance that conforms to the JSON schema below. JSON only, no explanation.

As an example, for the schema {{"properties": {{"foo": {{"description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:
```
{{'$defs': {{'Finding': {{'properties': {{'summary': {{'description': '洞察总结', 'title': 'Summary', 'type': 'string'}}, 'explanation': {{'description': '洞察解释,并满足论证规则要求。', 'title': 'Explanation', 'type': 'string'}}}}, 'required': ['summary', 'explanation'], 'title': 'Finding', 'type': 'object'}}}}, 'properties': {{'title': {{'description': '报告标题', 'title': 'Title', 'type': 'string'}}, 'summary': {{'description': '报告摘要', 'title': 'Summary', 'type': 'string'}}, 'rating': {{'description': '影响严重性评级', 'title': 'Rating', 'type': 'number'}}, 'rating_explanation': {{'description': '影响严重性评级说明', 'title': 'Rating Explanation', 'type': 'string'}}, 'findings': {{'description': '报告发现', 'items': {{'$ref': '#/$defs/Finding'}}, 'title': 'Findings', 'type': 'array'}}}}, 'required': ['title', 'summary', 'rating', 'rating_explanation', 'findings'], 'title': 'CommunityReport', 'type': 'object'}}
```

### 示例

输入文本:
-----Entities-----
```csv
id,实体,描述
5,翠绿绿洲广场,翠绿绿洲广场是团结大游行的举办地点
6,和谐集会,和谐集会是在翠绿绿洲广场举行游行的组织
```

-----Relationships-----
```csv
id,源,目标,描述
37,翠绿绿洲广场,团结大游行,翠绿绿洲广场是团结大游行的举办地点
38,翠绿绿洲广场,和谐集会,和谐集会在翠绿绿洲广场举行游行
39,翠绿绿洲广场,团结大游行,团结大游行在翠绿绿洲广场举行
40,翠绿绿洲广场,论坛聚焦,论坛聚焦正在报道在翠绿绿洲广场举行的团结大游行
41,翠绿绿洲广场,贝利·阿萨迪,贝利·阿萨迪在翠绿绿洲广场就游行发表讲话
43,和谐集会,团结大游行,和谐集会正在组织团结大游行
```

输出:
```json
{{
    "title": "翠绿绿洲广场和团结大游行",
    "summary": "该社区以翠绿绿洲广场为中心，它是团结大游行的举办地点。该广场与和谐集会、团结大游行和论坛聚焦有关联，这些都与游行事件相关。",
    "rating": 5.0,
    "rating_explanation": "影响严重性评级为中等，这是由于团结大游行期间可能出现的动乱或冲突。",
    "findings": [
        {{
            "summary": "翠绿绿洲广场作为中心地点",
            "explanation": "翠绿绿洲广场是该社区的核心实体，作为团结大游行的举办地点。这个广场是所有其他实体之间的共同联系点，表明它在社区中的重要性。广场与游行的关联可能会导致公共秩序问题或冲突，这取决于游行的性质和引发的反应。[数据: 实体 (5), 关系 (37, 38, 39, 40, 41,+更多)]"
        }},
        {{
            "summary": "和谐集会在社区中的作用",
            "explanation": "和谐集会是该社区的另一个关键实体，是在翠绿绿洲广场组织游行的机构。和谐集会及其游行的性质可能是潜在威胁的来源，这取决于他们的目标和引发的反应。和谐集会与广场之间的关系对理解这个社区的动态至关重要。[数据: 实体 (6), 关系 (38, 43)]"
        }},
        {{
            "summary": "团结大游行作为重要事件",
            "explanation": "团结大游行是在翠绿绿洲广场举行的一项重要事件。这个事件是社区动态的一个关键因素，可能是潜在威胁的来源，这取决于游行的性质和引发的反应。游行与广场之间的关系对理解这个社区的动态至关重要。[数据: 关系 (39)]"
        }},
        {{
            "summary": "论坛聚焦的角色",
            "explanation": "论坛聚焦正在报道在翠绿绿洲广场举行的团结大游行。这表明该事件已经引起了媒体的关注，可能会放大其对社区的影响。论坛聚焦的角色可能在塑造公众对事件和相关实体的看法方面具有重要意义。[数据: 关系 (40)]"
        }}
    ]
}}
```

### 真实数据使用指南

请使用以下文本作为您的输入数据。切勿在回答中编造任何内容。

输入文本:

-----Entities-----
```csv
{entity_df}
```

-----Relationships-----
```csv
{relation_df}
```

### 报告结构
报告应包括以下部分：

1. 标题
   - 代表社区名称，反映其关键实体。
   - 标题应简短且具体，若可能，包含具有代表性的命名实体。

2. 摘要
   - 对社区整体结构的执行摘要。
   - 描述实体之间的相互关联及与实体相关的重要信息。

3. 影响严重性评级
   - 一个介于0-10之间的浮点数，代表社区内实体所构成的影响的严重程度。
   - 影响指社区评分的重要性。

4. 评级说明
   - 对影响严重性评级进行一句话解释。

5. 详细发现
   - 关于社区的5-10个关键洞察。
   - 每个洞察包括：
     - 总结：简短的洞察总结。
     - 解释：多个段落的解释性文本，依据以下基础规则进行论证，确保全面阐述。
     
### 输出格式
The output should be formatted as a JSON instance that conforms to the JSON schema below. JSON only, no explanation.

As an example, for the schema {{"properties": {{"foo": {{"description": "a list of strings", "type": "array", "items": {{"type": "string"}}}}}}, "required": ["foo"]}}
the object {{"foo": ["bar", "baz"]}} is a well-formatted instance of the schema. The object {{"properties": {{"foo": ["bar", "baz"]}}}} is not well-formatted.

Here is the output schema:
```
{{'$defs': {{'Finding': {{'properties': {{'summary': {{'description': '洞察总结', 'title': 'Summary', 'type': 'string'}}, 'explanation': {{'description': '洞察解释,并满足论证规则要求。', 'title': 'Explanation', 'type': 'string'}}}}, 'required': ['summary', 'explanation'], 'title': 'Finding', 'type': 'object'}}}}, 'properties': {{'title': {{'description': '报告标题', 'title': 'Title', 'type': 'string'}}, 'summary': {{'description': '报告摘要', 'title': 'Summary', 'type': 'string'}}, 'rating': {{'description': '影响严重性评级', 'title': 'Rating', 'type': 'number'}}, 'rating_explanation': {{'description': '影响严重性评级说明', 'title': 'Rating Explanation', 'type': 'string'}}, 'findings': {{'description': '报告发现', 'items': {{'$ref': '#/$defs/Finding'}}, 'title': 'Findings', 'type': 'array'}}}}, 'required': ['title', 'summary', 'rating', 'rating_explanation', 'findings'], 'title': 'CommunityReport', 'type': 'object'}}
```

### 论证规则
- 数据支持的观点：所有观点必须由数据支持，并按以下方式列出其数据引用。
- 引用格式：
  - 例如：“X人是Y公司的所有者，并受到许多不当行为的指控 [数据: 报告 (1), 实体 (5, 7); 关系 (23); 声明 (7, 2, 34, 64, 46, +更多)]。”
  - 在单个引用中列出不超过5个记录ID，最相关的前5个记录ID后添加“+更多”以表示还有更多。
- 避免：
  - 不要包含没有提供支持证据的信息。

Output:"""


GLOBAL_MAP_RAG_POINTS = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1...", "score": score_value}},
        {{"description": "Description of point 2...", "score": score_value}}
    ]
}}

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.


---Data tables---

{context_data}

---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1", "score": score_value}},
        {{"description": "Description of point 2", "score": score_value}}
    ]
}}
"""


FAIL_RESPONSE = "抱歉，我无法回答这个问题。"


GLOBAL_REDUCE_RAG_RESPONSE = """---Role---

您是一位乐于助人的助手，通过综合多位分析师的观点来回答有关数据集的问题。

---Goal---

生成符合目标长度和格式的回复，以响应用户的问题，并总结专注于数据集不同部分的**多位分析师的所有报告**。

请注意，下面提供的分析师报告**按重要性降序排列（最重要到最不重要）**。

如果您不知道答案，或者提供的报告不足以提供答案，请直接说明。**不要编造任何内容。**

最终回复应**移除分析师报告中所有不相关的信息**，并将清理后的信息合并成一个全面的答案，该答案应提供所有关键点及其含义的解释，并符合目标回复的长度和格式。

根据回复的长度和格式适当添加章节和评论。**使用markdown样式**。

回复应**保留原文中情态动词（如“应 (shall)”、“可能 (may)”或“将 (will)”）的含义和使用**。

**不要包含没有提供支持证据的信息。**

---Target response length and format---

{response_type}


---Analyst Reports---

{report_data}


---Goal---

生成符合目标长度和格式的回复，以响应用户的问题，并总结专注于数据集不同部分的**多位分析师的所有报告**。

请注意，下面提供的分析师报告**按重要性降序排列（最重要到最不重要）**。

如果您不知道答案，或者提供的报告不足以提供答案，请直接说明。**不要编造任何内容。**

最终回复应**移除分析师报告中所有不相关的信息**，并将清理后的信息合并成一个全面的答案，该答案应提供所有关键点及其含义的解释，并符合目标回复的长度和格式。

回复应**保留原文中情态动词（如“应 (shall)”、“可能 (may)”或“将 (will)”）的含义和使用**。

**不要包含没有提供支持证据的信息。**


---Target response length and format---

{response_type}

根据回复的长度和格式适当添加章节和评论。**使用markdown样式**。"""


MINIRAG_QUERY2KWD = """---Role---

You are a helpful assistant tasked with identifying both answer-type and low-level keywords in the user's query.

---Goal---

Given the query, list both answer-type and low-level keywords.
answer_type_keywords focus on the type of the answer to the certain query, while low-level keywords focus on specific entities, details, or concrete terms.
The answer_type_keywords must be selected from Answer type pool. 
This pool is in the form of a dictionary, where the key represents the Type you should choose from and the value represents the example samples.

---Instructions---

- Output the keywords in JSON format.
- The JSON should have three keys:
  - "answer_type_keywords" for the types of the answer. In this list, the types with the highest likelihood should be placed at the forefront. No more than 3.
  - "entities_from_query" for specific entities or details. It must be extracted from the query.
######################
-Examples-
######################
Example 1:

Query: "国际贸易如何影响全球经济稳定?"
Answer type pool: {{
 'PERSONAL LIFE': ['家庭时间', '家庭维护'],
 'STRATEGY': ['营销计划', '业务扩展'],
 'SERVICE FACILITATION': ['在线支持', '客户服务培训'],
 'PERSON': ['简·多伊', '约翰·史密斯'],
 'FOOD': ['意大利面', '寿司'],
 'EMOTION': ['快乐', '愤怒'],
 'PERSONAL EXPERIENCE': ['出国旅行', '海外留学'],
 'INTERACTION': ['团队会议', '社交活动'],
 'BEVERAGE': ['咖啡', '茶'],
 'PLAN':  ['年度预算', '项目时间表'],
 'GEO':  ['纽约市', '南非'],
 'GEAR': ['露营帐篷', '自行车头盔'],
 'EMOJI': ['🎉', '🚀'],
 'BEHAVIOR': ['积极反馈', '消极批评'],,
 'TONE': ['正式', '非正式'],
 'LOCATION': ['市中心', '郊区']
}}
################
Output:
{{
  "answer_type_keywords": ["STRATEGY","PERSONAL LIFE"],
  "entities_from_query": ["贸易协定", "关税", "货币兑换", "进口", "出口"]
}}
#############################
Example 2:

Query: "When was SpaceX's first rocket launch?"
Answer type pool: {{
 'DATE AND TIME': ['2023-10-10 10:00', 'THIS AFTERNOON'],
 'ORGANIZATION': ['GLOBAL INITIATIVES CORPORATION', 'LOCAL COMMUNITY CENTER'],
 'PERSONAL LIFE': ['DAILY EXERCISE ROUTINE', 'FAMILY VACATION PLANNING'],
 'STRATEGY': ['NEW PRODUCT LAUNCH', 'YEAR-END SALES BOOST'],
 'SERVICE FACILITATION': ['REMOTE IT SUPPORT', 'ON-SITE TRAINING SESSIONS'],
 'PERSON': ['ALEXANDER HAMILTON', 'MARIA CURIE'],
 'FOOD': ['GRILLED SALMON', 'VEGETARIAN BURRITO'],
 'EMOTION': ['EXCITEMENT', 'DISAPPOINTMENT'],
 'PERSONAL EXPERIENCE': ['BIRTHDAY CELEBRATION', 'FIRST MARATHON'],
 'INTERACTION': ['OFFICE WATER COOLER CHAT', 'ONLINE FORUM DEBATE'],
 'BEVERAGE': ['ICED COFFEE', 'GREEN SMOOTHIE'],
 'PLAN': ['WEEKLY MEETING SCHEDULE', 'MONTHLY BUDGET OVERVIEW'],
 'GEO': ['MOUNT EVEREST BASE CAMP', 'THE GREAT BARRIER REEF'],
 'GEAR': ['PROFESSIONAL CAMERA EQUIPMENT', 'OUTDOOR HIKING GEAR'],
 'EMOJI': ['📅', '⏰'],
 'BEHAVIOR': ['PUNCTUALITY', 'HONESTY'],
 'TONE': ['CONFIDENTIAL', 'SATIRICAL'],
 'LOCATION': ['CENTRAL PARK', 'DOWNTOWN LIBRARY']
}}

################
Output:
{{
  "answer_type_keywords": ["DATE AND TIME", "ORGANIZATION", "PLAN"],
  "entities_from_query": ["SpaceX", "Rocket launch", "Aerospace", "Power Recovery"]

}}
#############################
Example 3:

Query: "What is the role of education in reducing poverty?"
Answer type pool: {{
 'PERSONAL LIFE': ['MANAGING WORK-LIFE BALANCE', 'HOME IMPROVEMENT PROJECTS'],
 'STRATEGY': ['MARKETING STRATEGIES FOR Q4', 'EXPANDING INTO NEW MARKETS'],
 'SERVICE FACILITATION': ['CUSTOMER SATISFACTION SURVEYS', 'STAFF RETENTION PROGRAMS'],
 'PERSON': ['ALBERT EINSTEIN', 'MARIA CALLAS'],
 'FOOD': ['PAN-FRIED STEAK', 'POACHED EGGS'],
 'EMOTION': ['OVERWHELM', 'CONTENTMENT'],
 'PERSONAL EXPERIENCE': ['LIVING ABROAD', 'STARTING A NEW JOB'],
 'INTERACTION': ['SOCIAL MEDIA ENGAGEMENT', 'PUBLIC SPEAKING'],
 'BEVERAGE': ['CAPPUCCINO', 'MATCHA LATTE'],
 'PLAN': ['ANNUAL FITNESS GOALS', 'QUARTERLY BUSINESS REVIEW'],
 'GEO': ['THE AMAZON RAINFOREST', 'THE GRAND CANYON'],
 'GEAR': ['SURFING ESSENTIALS', 'CYCLING ACCESSORIES'],
 'EMOJI': ['💻', '📱'],
 'BEHAVIOR': ['TEAMWORK', 'LEADERSHIP'],
 'TONE': ['FORMAL MEETING', 'CASUAL CONVERSATION'],
 'LOCATION': ['URBAN CITY CENTER', 'RURAL COUNTRYSIDE']
}}

################
Output:
{{
  "answer_type_keywords": ["STRATEGY", "PERSON"],
  "entities_from_query": ["School access", "Literacy rates", "Job training", "Income inequality"]
}}
#############################
Example 4:

Query: "Where is the capital of the United States?"
Answer type pool: {{
 'ORGANIZATION': ['GREENPEACE', 'RED CROSS'],
 'PERSONAL LIFE': ['DAILY WORKOUT', 'HOME COOKING'],
 'STRATEGY': ['FINANCIAL INVESTMENT', 'BUSINESS EXPANSION'],
 'SERVICE FACILITATION': ['ONLINE SUPPORT', 'CUSTOMER SERVICE TRAINING'],
 'PERSON': ['ALBERTA SMITH', 'BENJAMIN JONES'],
 'FOOD': ['PASTA CARBONARA', 'SUSHI PLATTER'],
 'EMOTION': ['HAPPINESS', 'SADNESS'],
 'PERSONAL EXPERIENCE': ['TRAVEL ADVENTURE', 'BOOK CLUB'],
 'INTERACTION': ['TEAM BUILDING', 'NETWORKING MEETUP'],
 'BEVERAGE': ['LATTE', 'GREEN TEA'],
 'PLAN': ['WEIGHT LOSS', 'CAREER DEVELOPMENT'],
 'GEO': ['PARIS', 'NEW YORK'],
 'GEAR': ['CAMERA', 'HEADPHONES'],
 'EMOJI': ['🏢', '🌍'],
 'BEHAVIOR': ['POSITIVE THINKING', 'STRESS MANAGEMENT'],
 'TONE': ['FRIENDLY', 'PROFESSIONAL'],
 'LOCATION': ['DOWNTOWN', 'SUBURBS']
}}
################
Output:
{{
  "answer_type_keywords": ["LOCATION"],
  "entities_from_query": ["capital of the United States", "Washington", "New York"]
}}
#############################

-Real Data-
######################
Query: {query}
Answer type pool:{TYPE_POOL}
######################
Output:

"""


LOCAL_RAG_RESPONSE = """---Role---

你是一个乐于助人的助手，负责回答用户关于所提供数据表中数据的问题。


---Goal---

生成符合目标长度和格式的回复，回应用户的问题。回复应：
1.  总结输入数据表中所有相关信息，其详尽程度需适合目标响应长度和格式。
2.  纳入任何相关的常识性知识。
3.  如果不知道答案，直接说明不知道。
4.  **切勿编造信息。**
5.  **未提供支持证据的信息不得包含在内。**

---Target response length and format---

{response_type}


---Data tables---

{context_data}


---Goal---

生成符合目标长度和格式的回复，回应用户的问题。回复应：
1.  总结输入数据表中所有相关信息，其详尽程度需适合目标响应长度和格式。
2.  纳入任何相关的常识性知识。
3.  如果不知道答案，直接说明不知道。
4.  **切勿编造信息。**
5.  **未提供支持证据的信息不得包含在内。**


---Target response length and format---

{response_type}

**（新增要求）**
1.  根据目标长度和格式的需要，在回复中添加适当的章节和评述。
2.  **使用markdown格式化响应。**

"""
