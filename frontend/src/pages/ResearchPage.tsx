import {
  ExperimentOutlined,
  FlagOutlined,
  TrophyOutlined,
} from "@ant-design/icons";
import {
  Button,
  Card,
  Checkbox,
  Col,
  Progress,
  Row,
  Tag,
  Typography,
  message,
} from "antd";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  CLASS_META,
  CLASS_RESEARCH_PUBLIC,
  SAMPLE_ACCOUNTS,
  TANG_RESEARCH_PROFILE,
} from "../data/roster2501";
import { useAuthStore } from "../stores/useAuthStore";

const CHECK_KEY = "gongke-research-checks-v1";

export function ResearchPage() {
  const user = useAuthStore((s) => s.user);
  const isTang =
    user?.username === TANG_RESEARCH_PROFILE.studentId ||
    user?.display_name === TANG_RESEARCH_PROFILE.name;

  const [checks, setChecks] = useState<Record<string, boolean>>(() => {
    try {
      const raw = localStorage.getItem(CHECK_KEY);
      if (raw) return JSON.parse(raw) as Record<string, boolean>;
    } catch {
      /* ignore */
    }
    return Object.fromEntries(
      TANG_RESEARCH_PROFILE.checklist.map((item) => [item.id, item.done]),
    );
  });

  useEffect(() => {
    localStorage.setItem(CHECK_KEY, JSON.stringify(checks));
  }, [checks]);

  const tangSample = useMemo(
    () => SAMPLE_ACCOUNTS.find((a) => a.track === "research"),
    [],
  );

  const toggle = (id: string) => {
    if (!isTang) {
      message.info("请使用样例账号「唐铭鑫」登录后勾选个人清单");
      return;
    }
    setChecks((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="research-page">
      <section className="class-hero">
        <p className="eyebrow">工试共创空间 · 科研与竞赛</p>
        <Typography.Title level={2}>科研与竞赛共创板</Typography.Title>
        <Typography.Paragraph>
          {CLASS_META.name} 的公开成果与个人课题看板。班级层面向全员可见；个人清单以样例账号{" "}
          <strong>唐铭鑫</strong> 演示共创推进。
        </Typography.Paragraph>
        <div className="class-hero__actions">
          <Link to="/class">
            <Button>返回班级页</Button>
          </Link>
          {!isTang && tangSample ? (
            <Typography.Text type="secondary">
              演示账号：{tangSample.name} / {tangSample.studentId}（密码 {tangSample.password}）
            </Typography.Text>
          ) : (
            <Tag color="green">当前：{user?.display_name} · 可编辑个人清单</Tag>
          )}
        </div>
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <TrophyOutlined />
          <Typography.Title level={3}>班级成果墙</Typography.Title>
        </div>
        <Typography.Paragraph type="secondary">
          {CLASS_RESEARCH_PUBLIC.summary}
        </Typography.Paragraph>
        <div className="class-fact-row">
          {CLASS_RESEARCH_PUBLIC.metrics.map((item) => (
            <div key={item.label} className="class-fact">
              <small>{item.label}</small>
              <strong>{item.value}</strong>
            </div>
          ))}
        </div>
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={12}>
            <Card className="class-board-card" bordered={false}>
              <Tag>竞赛</Tag>
              <Typography.Title level={4}>主要获奖</Typography.Title>
              <ul className="research-list">
                {CLASS_RESEARCH_PUBLIC.competitions.map((item) => (
                  <li key={item.name}>
                    <strong>{item.name}</strong>
                    <span>{item.award}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card className="class-board-card" bordered={false} style={{ marginBottom: 16 }}>
              <Tag>论文 / 专利 / 大创</Tag>
              <Typography.Title level={4}>成果摘要</Typography.Title>
              <ul className="research-list">
                {CLASS_RESEARCH_PUBLIC.papers.map((item) => (
                  <li key={item.title}>
                    <strong>{item.title}</strong>
                    <span>{item.note}</span>
                  </li>
                ))}
                {CLASS_RESEARCH_PUBLIC.patents.map((item) => (
                  <li key={item.title}>
                    <strong>{item.title}</strong>
                    <span>{item.note}</span>
                  </li>
                ))}
                {CLASS_RESEARCH_PUBLIC.projects.map((item) => (
                  <li key={item.title}>
                    <strong>{item.title}</strong>
                    <span>{item.note}</span>
                  </li>
                ))}
              </ul>
            </Card>
            <Card className="class-board-card" bordered={false}>
              <FlagOutlined /> 全员进组 · 导师月谈 · 竞赛经验分享会 5 次
            </Card>
          </Col>
        </Row>
      </section>

      <section className="class-section">
        <div className="class-section__head">
          <ExperimentOutlined />
          <Typography.Title level={3}>
            个人看板 · {TANG_RESEARCH_PROFILE.name}
          </Typography.Title>
        </div>
        <Typography.Paragraph type="secondary">
          {TANG_RESEARCH_PROFILE.role} · {TANG_RESEARCH_PROFILE.focus}
          <br />
          {TANG_RESEARCH_PROFILE.mentor}
        </Typography.Paragraph>
        <Row gutter={[16, 16]}>
          {TANG_RESEARCH_PROFILE.projects.map((proj) => (
            <Col key={proj.id} xs={24} md={12}>
              <Card className="class-board-card" bordered={false}>
                <div className="class-announce-head">
                  <Typography.Title level={5}>{proj.title}</Typography.Title>
                  <Tag color="blue">{proj.status}</Tag>
                </div>
                <Progress percent={proj.progress} strokeColor="#2f8667" />
                <Typography.Paragraph type="secondary" style={{ marginBottom: 0 }}>
                  下一步：{proj.next}
                </Typography.Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} md={14}>
            <Card className="class-board-card" bordered={false}>
              <Typography.Title level={4}>赛事节点</Typography.Title>
              <div className="class-wall-list">
                {TANG_RESEARCH_PROFILE.contests.map((c) => (
                  <div key={c.id} className="research-contest">
                    <div className="class-announce-head">
                      <strong>{c.name}</strong>
                      <Tag>{c.stage}</Tag>
                    </div>
                    <Typography.Text type="secondary">截止：{c.due}</Typography.Text>
                    <Typography.Paragraph style={{ marginBottom: 0 }}>{c.note}</Typography.Paragraph>
                  </div>
                ))}
              </div>
            </Card>
          </Col>
          <Col xs={24} md={10}>
            <Card className="class-board-card" bordered={false}>
              <Typography.Title level={4}>本周共创清单</Typography.Title>
              <div className="research-checklist">
                {TANG_RESEARCH_PROFILE.checklist.map((item) => (
                  <Checkbox
                    key={item.id}
                    checked={Boolean(checks[item.id])}
                    onChange={() => toggle(item.id)}
                  >
                    {item.text}
                  </Checkbox>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      </section>
    </div>
  );
}
