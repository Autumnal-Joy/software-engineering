import { Button, Card, PageHeader, Space } from "antd";
import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../../components/UserManager";
import "./Admin.css";

function Admin() {
  const auth = useAuth();

  const { username } = auth.userAuth;
  const navitage = useNavigate();

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
          <Link to="chargers">查看充电桩</Link>
        </Card>
        <Card>
          <Link to="table">查看报表</Link>
        </Card>
      </Space>
    </>
  );
}

export default Admin;
