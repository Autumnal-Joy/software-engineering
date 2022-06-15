import {
  Avatar,
  BackTop,
  Button,
  Card,
  Descriptions,
  Drawer,
  List,
  message,
  Space,
  Switch,
} from "antd";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../components/UserManager";
import { post } from "../../utils/net";
import Back from "../../components/back/Back";
import "./Chargers.css";

type UsersInfo = {
  username: number;
  chargeQuantity: boolean;
  waitingTime: number;
}[];

interface UsersInfoRes {
  message: string;
  data: UsersInfo;
}

function UsersDraw(props: {
  chargerID: string;
  visible: boolean;
  onClose: () => void;
}) {
  const [usersInfo, setUsersInfo] = useState<UsersInfo>([]);
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  useEffect(() => {
    props.chargerID &&
      post<UsersInfoRes>("adminGetUsers", {
        username,
        password,
        chargerID: props.chargerID.toString(),
      }).then(res => {
        setUsersInfo(res.data);
      });
  }, [password, props.chargerID, username]);

  return (
    <Drawer
      autoFocus
      forceRender
      onClose={props.onClose}
      placement="bottom"
      title={`充电桩#${props.chargerID}`}
      visible={props.visible}
    >
      <List
        dataSource={usersInfo}
        renderItem={user => (
          <List.Item key={user.username}>
            <Space direction="vertical" style={{ display: "flex" }}>
              <List.Item.Meta
                avatar={
                  <Avatar
                    src={`https://api.multiavatar.com/${user.username}.png`}
                  />
                }
                title={<a href="https://ant.design">{user.username}</a>}
              />
              <Descriptions>
                <Descriptions.Item label="充电量">
                  {user.chargeQuantity}度（kWH）
                </Descriptions.Item>
                <Descriptions.Item label="等待时间">
                  {(user.waitingTime / 36e5).toFixed(2)}小时
                </Descriptions.Item>
              </Descriptions>
            </Space>
          </List.Item>
        )}
      />
    </Drawer>
  );
}

type ChargersList = {
  chargerID: string;
  working: boolean;
  totalChargeCount: number;
  totalChargeTime: number;
  totalChargeQuantity: number;
}[];

interface ChargersRes {
  message: string;
  data: ChargersList;
}

function Chargers() {
  const [chargers, setChargers] = useState<ChargersList>();
  const [loadings, setLoadings] = useState<Record<string, boolean>>({});
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  function updateChargers() {
    post<ChargersRes>("adminGetChargers", { username, password })
      .then(res => {
        setChargers(res.data);
      })
      .catch(e => {
        message.error({ content: e.message, key: "adminGetChargers" });
      });
  }

  useEffect(updateChargers, [password, username]);

  function turnCharger(chargerID: string, turn: boolean) {
    setLoadings(loadings => {
      loadings[chargerID] = true;
      return loadings;
    });
    post<ChargersRes>("adminTurnCharger", {
      username,
      password,
      chargerID,
      turn: turn ? "on" : "off",
    })
      .then(updateChargers)
      .catch(e => {
        message.error({ content: e.message, key: "adminTurnCharger" });
      })
      .finally(() => {
        setLoadings(loadings => {
          loadings[chargerID] = false;
          return loadings;
        });
      });
  }

  const [usersDrawVisible, setUsersDrawVisible] = useState(false);
  const [chargerID, setChargerID] = useState("");

  return (
    <>
      <BackTop />
      <Back title="查看充电桩列表" />
      <UsersDraw
        chargerID={chargerID}
        visible={usersDrawVisible}
        onClose={() => {
          setUsersDrawVisible(false);
        }}
      />
      {chargers && (
        <Space direction="vertical" style={{ display: "flex" }}>
          {chargers.map(v => (
            <Card
              key={v.chargerID.toString()}
              title={`充电桩#${v.chargerID}`}
              extra={
                <Switch
                  checkedChildren="开启"
                  unCheckedChildren="关闭"
                  checked={v.working}
                  onClick={e => {
                    turnCharger(v.chargerID, e);
                  }}
                  loading={loadings[v.chargerID] || false}
                />
              }
            >
              <Descriptions>
                <Descriptions.Item label="充电次数">
                  {v.totalChargeCount}次
                </Descriptions.Item>
                <Descriptions.Item label="充电量">
                  {v.totalChargeQuantity}度（kWH）
                </Descriptions.Item>
                <Descriptions.Item label="充电时间">
                  {(v.totalChargeTime / 36e5).toFixed(2)}小时
                </Descriptions.Item>
              </Descriptions>
              <Button
                block
                onClick={() => {
                  setChargerID(v.chargerID);
                  setUsersDrawVisible(true);
                }}
              >
                查看充电桩#{v.chargerID}正在服务的对象
              </Button>
            </Card>
          ))}
        </Space>
      )}
    </>
  );
}

export default Chargers;
