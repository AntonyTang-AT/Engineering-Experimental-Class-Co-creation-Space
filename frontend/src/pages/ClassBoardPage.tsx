import { BookOutlined, CalendarOutlined, MessageOutlined } from "@ant-design/icons";
import { Button, Card, List, Tag, Typography } from "antd";
import { Link } from "react-router-dom";

import { CLASS_BOARD_ITEMS, CLASS_META } from "../data/roster2501";

const homework = [
  { course: "高等数学", due: "本周五", item: "极限综合练习 8 题 + 错因归类" },
  { course: "大学物理", due: "本周日", item: "斜面受力检查清单自测" },
  { course: "计概", due: "下周一二选一", item: "分支循环沙箱通过并整理 1 处报错" },
];

export function ClassBoardPage() {
  return (
    <div className="class-board-page">
      <section className="panel class-hero">
        <p className="eyebrow">班务共创</p>
        <Typography.Title level={2}>作业清单与协作入口</Typography.Title>
        <Typography.Paragraph>
          {CLASS_META.tagline}：班委维护清单，同学共享资料，AI 助手帮你压缩冲突、整理提醒。
        </Typography.Paragraph>
      </section>

      <section className="class-board-grid">
        <Card className="panel" bordered={false}>
          <Typography.Title level={4}>
            <CalendarOutlined /> 本周作业清单
          </Typography.Title>
          <List
            dataSource={homework}
            renderItem={(row) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <>
                      <Tag>{row.course}</Tag>
                      {row.item}
                    </>
                  }
                  description={`截止：${row.due}`}
                />
              </List.Item>
            )}
          />
        </Card>

        <Card className="panel" bordered={false}>
          <Typography.Title level={4}>协作快捷方式</Typography.Title>
          <div className="class-hero__actions">
            <Link to="/materials">
              <Button icon={<BookOutlined />}>共享复习资料</Button>
            </Link>
            <Link to="/chat">
              <Button type="primary" icon={<MessageOutlined />}>
                AI 班务 / 学业助手
              </Button>
            </Link>
            <Link to="/blackboard">
              <Button>个人提醒板</Button>
            </Link>
            <Link to="/class">
              <Button>返回成员墙</Button>
            </Link>
          </div>
          <List
            style={{ marginTop: 16 }}
            dataSource={CLASS_BOARD_ITEMS}
            renderItem={(item) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <>
                      <Tag>{item.tag}</Tag>
                      {item.title}
                    </>
                  }
                  description={item.body}
                />
              </List.Item>
            )}
          />
        </Card>
      </section>
    </div>
  );
}
