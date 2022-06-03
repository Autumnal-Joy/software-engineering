import { BackTop, Card, Descriptions, Drawer, List, message } from "antd";
import React, { useEffect, useState } from "react";
import { useAuth } from "../../components/UserManager";
import { post } from "../../utils/net";
import Back from "../back/Back";
import "./Bills.css";

interface BillInfo {
  billID: number;
  billTime: number;
  chargerID: number;
  chargeQuantity: number;
  chargeTime: number;
  startTime: number;
  endTime: number;
  chargeCost: number;
  serviceCost: number;
  cost: number;
}

interface BillInfoRes {
  message: string;
  data: BillInfo;
}

function BillDraw(props: {
  billID: number;
  visible: boolean;
  onClose: () => void;
}) {
  const [billInfo, setBillInfo] = useState({} as BillInfo);
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  useEffect(() => {
    props.billID &&
      post<BillInfoRes>("userGetBill", {
        username,
        password,
        billID: props.billID,
      }).then(res => {
        setBillInfo(res.data);
      });
  }, [password, props.billID, username]);

  return (
    <Drawer
      autoFocus
      forceRender
      onClose={props.onClose}
      placement="bottom"
      title={`详单#${props.billID}`}
      visible={props.visible}
    >
      <Descriptions>
        <Descriptions.Item label="详单时间">
          {new Date(billInfo.billTime).toLocaleString()}
        </Descriptions.Item>
        <Descriptions.Item label="充电桩编号">
          #{billInfo.chargerID}
        </Descriptions.Item>
        <Descriptions.Item label="充电量">
          {billInfo.chargeQuantity}度
        </Descriptions.Item>
        <Descriptions.Item label="充电时长">
          {(billInfo.chargeTime / 36e5).toFixed(2)}小时
        </Descriptions.Item>
        <Descriptions.Item label="充电开始时间">
          {new Date(billInfo.startTime).toLocaleString()}
        </Descriptions.Item>
        <Descriptions.Item label="充电结束时间">
          {new Date(billInfo.endTime).toLocaleString()}
        </Descriptions.Item>
        <Descriptions.Item label="充电费用">
          {billInfo.chargeCost} 人民币（CNY）
        </Descriptions.Item>
        <Descriptions.Item label="服务费用">
          {billInfo.serviceCost} 人民币（CNY）
        </Descriptions.Item>
        <Descriptions.Item label="费用总计">
          {billInfo.cost} 人民币（CNY）
        </Descriptions.Item>
      </Descriptions>
    </Drawer>
  );
}

type BillsList = {
  billID: number;
  billTime: number;
  chargeQuantity: number;
}[];

interface BillsListRes {
  message: string;
  data: BillsList;
}

function Bills() {
  const [billList, setBillList] = useState([] as BillsList);
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  useEffect(() => {
    post<BillsListRes>("userGetBillsList", { username, password })
      .then(res => {
        setBillList(res.data);
      })
      .catch(e => {
        message.error({ content: e.message, key: "userGetOrder" });
      });
  }, [password, username]);

  const [billDrawVisible, setBillDrawVisible] = useState(false);
  const [billID, setBillID] = useState(0);

  return (
    <>
      <BackTop />
      <Back title="充电详单" />
      <BillDraw
        billID={billID}
        visible={billDrawVisible}
        onClose={() => {
          setBillDrawVisible(false);
        }}
      />
      <List
        size="large"
        bordered
        dataSource={billList}
        renderItem={item => (
          <List.Item>
            <Card
              bordered={false}
              hoverable
              style={{ width: "100%" }}
              title={`详单#${item.billID}`}
              onClick={() => {
                setBillID(item.billID);
                setBillDrawVisible(true);
              }}
            >
              <Descriptions>
                <Descriptions.Item label="详单时间">
                  {new Date(item.billTime).toLocaleString()}
                </Descriptions.Item>
                <Descriptions.Item label="充电量">
                  {item.chargeQuantity}度
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </List.Item>
        )}
      />
    </>
  );
}

export default Bills;
