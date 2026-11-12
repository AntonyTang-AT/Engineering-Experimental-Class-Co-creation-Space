import {
  BookOutlined,
  GithubOutlined,
  NotificationOutlined,
  PictureOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import {
  Button,
  Card,
  Col,
  Image,
  Input,
  Row,
  Tag,
  Typography,
  message,
} from "antd";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  CLASS_BOARD_ITEMS,
  CLASS_GALLERY,
  CLASS_META,
  CLASS_PUBLIC_INFO,
  CLASS_SHARED_CONTRIBS,
  CLASS_WALL_SEED,
  ROSTER_2501,
  SAMPLE_ACCOUNTS,
} from "../data/roster2501";
import { useAuthStore } from "../stores/useAuthStore";

type WallPost = {
  id: string;
  author: string;
  text: string;
  at: string;
};

const WALL_KEY = "gongke-class-wall-v1";

function loadWall(): WallPost[] {
  try {
    const raw = localStorage.getItem(WALL_KEY);
    if (!raw) return [...CLASS_WALL_SEED];
    const parsed = JSON.parse(raw) as WallPost[];
    return Array.isArray(parsed) && parsed.length ? parsed : [...CLASS_WALL_SEED];
  } catch {
    return [...CLASS_WALL_SEED];
  }
}

function formatNow() {
  const d = new Date();
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  return `今天 ${hh}:${mm}`;
}

export function ClassPage() {
  const user = useAuthStore((state) => state.user);
  const sampleIds = new Set<string>(
    SAMPLE_ACCOUNTS.map((item) => item.studentId),
  );
  const [wall, setWall] = useState<WallPost[]>(() => loadWall());
  const [draft, setDraft] = useState("");

  useEffect(() => {
    localStorage.setItem(WALL_KEY, JSON.stringify(wall));
  }, [wall]);

  const publish = () => {
    const text = draft.trim();
    if (!text) {
      message.warning("先写一句想和同学同步的内容");
      return;
    }
    const post: WallPost = {
      id: `wall-${Date.now()}`,
      author: user?.display_name || "同学",
      text,
      at: formatNow(),
    };
    setWall((prev) => [post, ...prev].slice(0, 40));
    setDraft("");
    message.success("已发布到共创留言墙");
  };

  return (
    <div className="class-page">
      <section className="class-hero">
        <p className="eyebrow">工试共创空间 · 班级页</p>
        <Typography.Title level={2}>{CLASS_META.name}</Typography.Title>
        <Typography.Paragraph>{CLASS_PUBLIC_INFO.intro}</Typography.Paragraph>
        <div className="class-fact-row">
          {CLASS_PUBLIC_INFO.facts.map((fact) => (
            <div key={fact.label} className="class-fact">
              <small>{fact.label}</small>
              <strong>{fact.value}</strong>
            </div>
          ))}
        </div>
        <div className="class-hero__actions">
          <Button type="primary" href={CLASS_META.githubUrl} target="_blank" rel="noreferrer">
            <GithubOutlined /> GitHub 开源
          </Button>
          <Link to="/blackboard">
            <Button>班务提醒</Button>
          </Link>
          <Link to="/materials">
            <Button icon={<BookOutlined />}>共享资料</Button>
          </Link>
        </div>
        {user?.display_name ? (
          <Typography.Text type="secondary">
            当前登录：{user.display_name}
            {user.username ? `（${user.username}）` : ""}
          </Typography.Text>
        ) : null}
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <NotificationOutlined />
          <Typography.Title level={3}>公共信息</Typography.Title>
        </div>
        <Typography.Paragraph type="secondary">
          面向全班可见的公告与班务说明（不含电话、寝室等隐私字段）。
        </Typography.Paragraph>
        <Row gutter={[16, 16]}>
          <Col xs={24} md={10}>
            <Card className="class-board-card" bordered={false}>
              <Tag>领航</Tag>
              <Typography.Title level={4}>双班主任</Typography.Title>
              <ul className="class-advisor-list">
                {CLASS_PUBLIC_INFO.advisors.map((item) => (
                  <li key={item.name}>
                    <strong>{item.name}</strong>
                    <span>{item.role}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </Col>
          <Col xs={24} md={14}>
            <div className="class-announce-list">
              {CLASS_PUBLIC_INFO.announcements.map((item) => (
                <Card key={item.title} className="class-board-card" bordered={false}>
                  <div className="class-announce-head">
                    <Typography.Title level={5}>{item.title}</Typography.Title>
                    <Tag>{item.when}</Tag>
                  </div>
                  <Typography.Paragraph type="secondary" style={{ marginBottom: 0 }}>
                    {item.detail}
                  </Typography.Paragraph>
                </Card>
              ))}
            </div>
          </Col>
        </Row>
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <PictureOutlined />
          <Typography.Title level={3}>班级影集</Typography.Title>
        </div>
        <Typography.Paragraph type="secondary">
          选自十佳班级答辩 PPT 的活动影像，展示集体协作与公共生活瞬间。
        </Typography.Paragraph>
        <Image.PreviewGroup>
          <div className="class-gallery">
            {CLASS_GALLERY.map((item) => (
              <figure key={item.src} className="class-gallery__item">
                <Image src={item.src} alt={item.title} />
                <figcaption>
                  <strong>{item.title}</strong>
                  <span>{item.caption}</span>
                </figcaption>
              </figure>
            ))}
          </div>
        </Image.PreviewGroup>
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <Typography.Title level={3}>共创留言墙</Typography.Title>
        </div>
        <Typography.Paragraph type="secondary">
          全班可见：同步作业冲突、资料补充、活动召集。发布后会出现在公共留言流里。
        </Typography.Paragraph>
        <Card className="class-board-card class-wall-composer" bordered={false}>
          <Input.TextArea
            rows={3}
            maxLength={200}
            showCount
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder="写一句想和全班同步的话，例如：今晚自习室拼桌 / 补充一道错题…"
          />
          <div className="class-wall-composer__actions">
            <Typography.Text type="secondary">
              将以 {user?.display_name || "同学"} 的名义发布
            </Typography.Text>
            <Button type="primary" onClick={publish}>
              发布到留言墙
            </Button>
          </div>
        </Card>
        <div className="class-wall-list">
          {wall.map((post) => (
            <Card key={post.id} className="class-board-card" bordered={false}>
              <div className="class-announce-head">
                <Typography.Text strong>{post.author}</Typography.Text>
                <Typography.Text type="secondary">{post.at}</Typography.Text>
              </div>
              <Typography.Paragraph style={{ marginBottom: 0 }}>{post.text}</Typography.Paragraph>
            </Card>
          ))}
        </div>
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <Typography.Title level={3}>资料共创认领</Typography.Title>
        </div>
        <Typography.Paragraph type="secondary">
          谁贡献了什么一目了然，把「共享」变成可追踪的共创。
        </Typography.Paragraph>
        <Row gutter={[16, 16]}>
          {CLASS_SHARED_CONTRIBS.map((item) => (
            <Col key={item.title} xs={24} sm={12} md={6}>
              <Card className="class-board-card" bordered={false}>
                <Tag>{item.kind}</Tag>
                <Typography.Title level={5}>{item.title}</Typography.Title>
                <Typography.Paragraph type="secondary">{item.note}</Typography.Paragraph>
                <Typography.Text>贡献者 · {item.by}</Typography.Text>
              </Card>
            </Col>
          ))}
        </Row>
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <TeamOutlined />
          <Typography.Title level={3}>成员墙</Typography.Title>
        </div>
        <Typography.Paragraph type="secondary">
          仅公开展示姓名。样例账号可演示完整学业共创流程。
        </Typography.Paragraph>
        <div className="member-wall">
          {ROSTER_2501.map((member) => {
            const isSample = sampleIds.has(member.studentId);
            return (
              <div
                key={member.studentId}
                className={`member-card${isSample ? " member-card--sample" : ""}`}
              >
                <strong>{member.name}</strong>
                {isSample ? <Tag color="green">样例</Tag> : null}
              </div>
            );
          })}
        </div>
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <Typography.Title level={3}>班务共创</Typography.Title>
        </div>
        <Row gutter={[16, 16]}>
          {CLASS_BOARD_ITEMS.map((item) => (
            <Col key={item.id} xs={24} md={8}>
              <Card className="class-board-card" bordered={false}>
                <Tag>{item.tag}</Tag>
                <Typography.Title level={4}>{item.title}</Typography.Title>
                <Typography.Paragraph type="secondary">{item.body}</Typography.Paragraph>
                {"link" in item && item.link ? (
                  <Link to={item.link}>进入 →</Link>
                ) : null}
              </Card>
            </Col>
          ))}
        </Row>
      </section>
    </div>
  );
}
