import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Card, Checkbox, Form, Input, message, PageHeader } from "antd";
import CryptoJS from "crypto-js";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/UserManager";
import { post } from "../../utils/net";
import "./Login.css";

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
  const key = "loading";

  const [cardkey, setCardkey] = useState("userLogin");
  const navigate = useNavigate();
  const auth = useAuth();

  useEffect(() => {
    const { username, password, role } = auth.userAuth;
    if (!username) return;

    let [method, route] = ["userLogin", "/user"];
    if (role === "admin") {
      method = "adminLogin";
      route = "/admin";
    }
    post(method, {
      username: username,
      password: password,
    })
      .then(() => {
        navigate(route);
      })
      .catch(() => {
        return;
      });
  }, [auth.userAuth, navigate]);

  const onFinish = (values: {
    username: string;
    password: string;
    remember: boolean;
  }) => {
    message.loading({ content: "处理中...", duration: 0, key });

    const { username, password: rawPassword, remember } = values;
    const password = CryptoJS.MD5(rawPassword).toString();

    post(cardkey, { username, password })
      .then(() => {
        let route;
        if (cardkey === "adminLogin") {
          route = "/admin";
          auth.save({ username, password, role: "admin" }, remember);
        } else {
          route = "/user";
          auth.save({ username, password, role: "user" }, remember);
        }
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
          <Form.Item name="remember" valuePropName="checked">
            <Checkbox>记住我</Checkbox>
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
