import { Button, Card, PageHeader, Space } from "antd";
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../components/UserManager";
import "./User.css";

function User() {
  const navitage = useNavigate();
  const auth = useAuth();

  const username = auth.userAuth.username;

  function logout() {
    auth.delete();
    navitage("/");
  }

  return (
    <>
      <Space direction="vertical" style={{ display: "flex" }}>
        <PageHeader
          backIcon={false}
          avatar={{
            src: `https://api.multiavatar.com/${username}.png`,
          }}
          title={`${username}`}
          extra={
            <Button onClick={logout} danger>
              退出登录
            </Button>
          }
        />
        <Card>
          <Link to="make-order">预约排号</Link>
        </Card>
        <Card>
          <Link to="order-info">查看当前预约</Link>
        </Card>
        <Card>
          <Link to="bills">查看充电详单</Link>
        </Card>
      </Space>
    </>
  );
}

export default User;
