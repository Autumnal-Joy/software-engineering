import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Card, Form, Input, message, PageHeader } from "antd";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { post } from "../../utils";
import "./Login.css";
import CryptoJS from "crypto-js";

const tabListNoTitle = [
  {
    key: "userLogin",
    tab: "用户登录",
  },
  {
    key: "userRegister",
    tab: "用户注册",
  },
  {
    key: "adminLogin",
    tab: "管理员登录",
  },
];

function Login() {
  const [cardkey, setCardkey] = useState("userLogin");
  const navigate = useNavigate();
  const key = "loading";

  const onFinish = (values: { username: string; password: string }) => {
    message.loading({ content: "处理中...", duration: 0, key });
    const { username, password: rawPassword } = values;
    const password = CryptoJS.MD5(rawPassword).toString();
    post(cardkey, { username, password })
      .then(() => {
        let route;
        if (cardkey === "adminLogin") {
          route = "/admin";
        } else {
          route = "/user";
        }
        window.localStorage.setItem("username", username);
        window.localStorage.setItem("password", password);
        message.success({ content: "登录成功", key });
        navigate(route);
      })
      .catch(e => {
        message.error({ content: e.message, key });
      });
  };

  return (
    <>
      <PageHeader backIcon={false} title="充电桩预约系统" />
      <Card
        tabList={tabListNoTitle}
        activeTabKey={cardkey}
        onTabChange={setCardkey}
      >
        <Form name="normal_login" size="large" onFinish={onFinish}>
          <Form.Item
            name="username"
            rules={[
              { required: true, message: "请输入用户名" },
              {
                pattern: /^[0-9a-zA-Z_]+$/,
                message: "用户名不合法",
              },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: "请输入密码" }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit">
              确认
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </>
  );
}

export default Login;
