/** 工试2501 花名册与班级共创数据（仅姓名等可公开信息） */
export const CLASS_META = {
  name: "工科试验班（人工智能类）2501",
  tagline: "敢为人先 · AI 赋能班务、学业与科研竞赛",
  githubUrl:
    "https://github.com/AntonyTang-AT/Engineering-Experimental-Class-Co-creation-Space",
  college: "湖南大学人工智能与机器人学院",
} as const;

export const ROSTER_2501 = [
  { studentId: "202511020106", name: "宋雨谦" },
  { studentId: "202593020922", name: "朱明耀" },
  { studentId: "202516010406", name: "范文孝" },
  { studentId: "202507020123", name: "王磊" },
  { studentId: "202593020403", name: "张思睿" },
  { studentId: "202593020422", name: "林锦睿" },
  { studentId: "202508011219", name: "雷鹏" },
  { studentId: "202507020332", name: "康宸睿" },
  { studentId: "202504100204", name: "周泓萱" },
  { studentId: "202593020322", name: "刘冬洋" },
  { studentId: "202593020126", name: "唐铭鑫" },
  { studentId: "202593020415", name: "郭可威" },
  { studentId: "202593020714", name: "赵军阳" },
  { studentId: "202593020614", name: "陈梁龙" },
  { studentId: "202593020914", name: "刘博文" },
  { studentId: "202593020616", name: "何文强" },
  { studentId: "202511020112", name: "董苏仪" },
  { studentId: "202507020403", name: "郝梓博" },
  { studentId: "202593020409", name: "汪佳文" },
  { studentId: "202593020420", name: "杜松联" },
] as const;

/** 评审样例账号 */
export const SAMPLE_ACCOUNTS = [
  {
    studentId: "202593020403",
    name: "张思睿",
    password: "020403",
    hint: "高数期末 · 计划冲突",
    track: "math" as const,
  },
  {
    studentId: "202593020409",
    name: "汪佳文",
    password: "020409",
    hint: "大物跟课 · 题目质疑",
    track: "physics" as const,
  },
  {
    studentId: "202507020403",
    name: "郝梓博",
    password: "020403",
    hint: "计概 Python · 沙箱练习",
    track: "cs" as const,
  },
  {
    studentId: "202593020126",
    name: "唐铭鑫",
    password: "020126",
    hint: "科研与竞赛 · 课题进度",
    track: "research" as const,
  },
] as const;

export const CLASS_PUBLIC_INFO = {
  intro:
    "我们是湖南大学首届工科试验班（人工智能类）。敢闯敢试敢为人先——全员进组、互学互助，并用 AI 把班务、学业与科研竞赛放进同一共创空间。",
  facts: [
    { label: "班级规模", value: "20 人" },
    { label: "科研参与", value: "100% 进组" },
    { label: "必修加权", value: "86.34 分" },
    { label: "国奖人次", value: "16 人次" },
  ],
  advisors: [
    { name: "王耀南", role: "班主任 · 中国工程院院士 · 方向引领" },
    { name: "江未来", role: "班主任 · 生活与日常关心" },
  ],
  announcements: [
    {
      title: "班委每周发布作业清单",
      detail: "明确各科完成时间，减少信息分散。",
      when: "每周",
    },
    {
      title: "共享复习资料",
      detail: "临近考试同学互传笔记与错题整理，资料页可按章节查阅。",
      when: "考前",
    },
    {
      title: "科研竞赛经验分享",
      detail: "已组织 5 次学长分享；全员在团队中深度参与课题或赛事。",
      when: "持续",
    },
    {
      title: "共创空间上线",
      detail: "学号登录即可使用班务、学业与科研竞赛工作台。",
      when: "当前",
    },
  ],
} as const;

export const CLASS_BOARD_ITEMS = [
  {
    id: "hw-week",
    title: "本周作业清单",
    body: "高数：极限综合；大物：受力检查清单；计概：分支循环沙箱。",
    tag: "班务",
  },
  {
    id: "share-review",
    title: "共享复习资料",
    body: "错题与笔记按章节共创认领，可在资料页继续查阅。",
    tag: "共创",
    link: "/materials",
  },
  {
    id: "research-board",
    title: "科研与竞赛板",
    body: "课题进度、赛事节点与组队信息；样例账号唐铭鑫可演示。",
    tag: "科研",
    link: "/research",
  },
] as const;

export const CLASS_GALLERY = [
  {
    src: "/class/gallery/class-meeting.jpg",
    title: "班会合影",
    caption: "全班与老师合影，班务当面同步。",
  },
  {
    src: "/class/gallery/moments-collage.jpg",
    title: "班级瞬间",
    caption: "课堂讨论、竞赛组队、志愿实践与运动会。",
  },
  {
    src: "/class/gallery/graduation-gala.jpg",
    title: "学院晚会",
    caption: "人工智能与机器人学院集体活动留影。",
  },
  {
    src: "/class/gallery/campus-volunteer.jpg",
    title: "校园志愿",
    caption: "同学共同参与校园服务与接待。",
  },
  {
    src: "/class/gallery/sports-meet.jpg",
    title: "运动会",
    caption: "集体入场，展现班级凝聚力。",
  },
  {
    src: "/class/gallery/enrollment-talk.jpg",
    title: "招生分享",
    caption: "朋辈宣传，把班级故事讲给更多人。",
  },
] as const;

export const CLASS_SHARED_CONTRIBS = [
  {
    title: "高数极限错题整理",
    by: "张思睿",
    kind: "笔记",
    note: "按放缩方向 / 公式误用归类",
  },
  {
    title: "大物受力检查清单",
    by: "汪佳文",
    kind: "清单",
    note: "斜面题漏摩擦的自检步骤",
  },
  {
    title: "计概沙箱自测题",
    by: "郝梓博",
    kind: "练习",
    note: "分支循环易错点合集",
  },
  {
    title: "竞赛时间线与组队表",
    by: "唐铭鑫",
    kind: "科研",
    note: "RoboCup / 数模 / 大创节点",
  },
] as const;

export const CLASS_WALL_SEED = [
  {
    id: "seed-1",
    author: "张思睿",
    text: "本周作业清单已更新，有冲突的同学可以在留言墙说一声，我们一起改排期。",
    at: "今天 09:20",
  },
  {
    id: "seed-2",
    author: "唐铭鑫",
    text: "科研与竞赛板已开放：欢迎补充自己的课题进展和组队需求。",
    at: "昨天 21:05",
  },
  {
    id: "seed-3",
    author: "郝梓博",
    text: "计概沙箱自测题放进资料共创了，分支循环卡壳可以先看那一页。",
    at: "昨天 18:40",
  },
] as const;

/** 班级科研竞赛公共成果 */
export const CLASS_RESEARCH_PUBLIC = {
  summary:
    "全员走进实验室，从 0 到 1；导师月谈不少于 1 次。以下为班级可公开的成果摘要。",
  metrics: [
    { label: "顶会论文", value: "3 篇" },
    { label: "发明专利", value: "2 项" },
    { label: "大创项目", value: "2 项" },
    { label: "国奖人次", value: "16" },
  ],
  competitions: [
    { name: "中国机器人大赛（RoboCup）", award: "一等奖（全国季军）" },
    { name: "机械工程创新创意大赛 · 智能制造", award: "一等奖" },
    { name: "全国大学生数学建模竞赛", award: "国家级二等奖" },
    { name: "全国大学生英语竞赛（NECCS）C 类", award: "三等奖" },
    { name: "ICPC 亚洲区域赛（沈阳）", award: "铜奖" },
    { name: "ACM MM 2026", award: "竞赛一等奖" },
    { name: "美赛（MCM/ICM）", award: "M 奖" },
  ],
  papers: [
    { title: "机器人领域顶会论文", note: "班级累计 3 篇（公开摘要）" },
  ],
  patents: [
    { title: "国家级发明专利", note: "累计 2 项" },
  ],
  projects: [
    { title: "国家级大创", note: "2 项 · 含负责人与核心成员" },
  ],
} as const;

/** 唐铭鑫样例：个人科研竞赛看板 */
export const TANG_RESEARCH_PROFILE = {
  name: "唐铭鑫",
  studentId: "202593020126",
  role: "课题成员 · 竞赛共创样例",
  focus: "具身智能相关课题推进 + 学科竞赛节点管理",
  mentor: "导师月谈 · 本月已完成 1 次进展沟通",
  projects: [
    {
      id: "proj-embodied",
      title: "具身智能方向课题",
      status: "进行中",
      progress: 62,
      next: "本周五前补齐实验记录与周报",
    },
    {
      id: "proj-dachuang",
      title: "国家级大创（核心成员）",
      status: "推进中",
      progress: 48,
      next: "与负责人对齐中期检查材料",
    },
  ],
  contests: [
    {
      id: "c-robocup",
      name: "RoboCup / 机器人相关赛事复盘",
      stage: "经验沉淀",
      due: "持续",
      note: "整理可复用的调试清单，供下学期新队员。",
    },
    {
      id: "c-mcm",
      name: "数模 / 美赛赛季准备",
      stage: "组队中",
      due: "两周内",
      note: "确认建模 / 写作 / 编程分工，预留周末集训。",
    },
  ],
  checklist: [
    { id: "ck1", text: "更新课题周报", done: true },
    { id: "ck2", text: "上传实验原始记录到共创板", done: false },
    { id: "ck3", text: "竞赛组队意向登记", done: true },
    { id: "ck4", text: "预约下次导师沟通", done: false },
  ],
} as const;
