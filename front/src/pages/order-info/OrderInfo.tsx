import {
  Button,
  Card,
  Descriptions,
  Empty,
  Form,
  InputNumber,
  message,
  Modal,
  Radio,
} from "antd";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/UserManager";
import { post } from "../../utils/net";
import Back from "../../components/back/Back";
import "./OrderInfo.css";

function ModifyChargeModel(props: {
  chargeType?: "F" | "T";
  chargeQuantity?: number;
  visible: boolean;
  setVisible: (visible: boolean) => void;
  setUpdate: () => void;
}) {
  const key = "modifyChargeModel";

  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  const modifyOrder = () => {
    form
      .validateFields()
      .then((values: { chargeType: string; chargeQuantity: number }) => {
        if (
          values.chargeType === props.chargeType &&
          values.chargeQuantity === props.chargeQuantity
        ) {
          props.setVisible(false);
        } else {
          setLoading(true);
          message.loading({
            content: "处理中...",
            duration: 0,
            key,
          });
          let promise;
          if (values.chargeType !== props.chargeType) {
            promise = post("userSendChargeType", {
              username,
              password,
              ...values,
            });
          } else {
            promise = post("userSendChargeQuantity", {
              username,
              password,
              chargeQuantity: values.chargeQuantity,
            });
          }
          promise
            .then(() => {
              message
                .success({ content: "修改成功", key })
                .then(props.setUpdate);
              props.setVisible(false);
              setLoading(false);
            })
            .catch(e => {
              setLoading(false);
              message.error({ content: e.message, key });
            });
        }
      })
      .catch(e => console.log(e));
  };

  return (
    <Modal
      cancelText="取消"
      confirmLoading={loading}
      okText="确认"
      onCancel={() => props.setVisible(false)}
      onOk={modifyOrder}
      title="请修改充电类别或充电量"
      visible={props.visible}
    >
      <Form
        layout="vertical"
        form={form}
        initialValues={{
          chargeType: props.chargeType,
          chargeQuantity: props.chargeQuantity,
        }}
      >
        <Form.Item label="充电类别" name="chargeType">
          <Radio.Group>
            <Radio value="F">快充</Radio>
            <Radio value="T">慢充</Radio>
          </Radio.Group>
        </Form.Item>

        <Form.Item
          label="充电量"
          name="chargeQuantity"
          rules={[
            { required: true, message: "请输入充电量" },
            {
              type: "number",
              min: 1,
              message: "单次充电量最少1度电",
            },
            {
              type: "number",
              max: 100,
              message: "单次充电量最多100度电",
            },
          ]}
        >
          <InputNumber precision={0} addonAfter="度（kWH）" />
        </Form.Item>
      </Form>
    </Modal>
  );
}

function CancelChargeModel(props: {
  visible: boolean;
  setVisible: (visible: boolean) => void;
}) {
  const key = "cancelChargeModel";

  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  const cancelOrder = () => {
    setLoading(true);

    message.loading({
      content: "处理中...",
      duration: 0,
      key,
    });
    post("userSendCancelCharge", { username, password })
      .then(() => {
        message.success({ content: "取消成功", key });
        props.setVisible(false);
        setLoading(false);
        navigate(-1);
      })
      .catch(e => {
        setLoading(false);
        message.error({ content: e, key });
      });
  };
  return (
    <Modal
      cancelText="取消"
      confirmLoading={loading}
      okText="确认"
      okType="danger"
      onCancel={() => props.setVisible(false)}
      onOk={cancelOrder}
      title="确认取消预约吗？"
      visible={props.visible}
    >
      一旦取消预约，则需要重新预约排号
    </Modal>
  );
}

interface Order {
  chargeType: "F" | "T";
  chargeQuantity: number;
}
interface OrderRes {
  message: string;
  data: Order;
}

interface LineNoRes {
  message: string;
  data: {
    lineNo: string;
  };
}

interface RankRes {
  message: string;
  data: {
    rank: number;
    endingTime: number;
  };
}

function OrderInfo() {
  const [order, setOrder] = useState<Order>();
  const [update, setUpdate] = useState(false);
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  useEffect(() => {
    post<OrderRes>("userGetOrder", { username, password })
      .then(res => {
        setOrder(res.data);
      })
      .catch(e => {
        message.error({ content: e.message, key: "userGetOrder" });
      });
  }, [password, username, update]);

  const [lineNo, setLineNo] = useState("");
  useEffect(() => {
    post<LineNoRes>("userGetLineNo", { username, password })
      .then(res => {
        setLineNo(res.data.lineNo);
      })
      .catch(e => {
        message.error({ content: e.message, key: "userGetOrder" });
      });
  }, [password, username, update]);

  const [rank, setRank] = useState(-1);
  const [endingTime, setEndingTime] = useState(-1);
  useEffect(() => {
    const getRank = () => {
      post<RankRes>("userGetRank", { username, password })
        .then(res => {
          setRank(res.data.rank);
          setEndingTime(res.data.endingTime);
        })
        .catch(e => {
          message.error({ content: e.message, key: "userGetOrder" });
        });
    };

    getRank();
    const timer = setInterval(getRank, 10_000);

    return () => {
      clearInterval(timer);
    };
  }, [password, username, update]);

  const [cancelOrderVisible, setCancelOrderVisible] = useState(false);
  const [modifyOrderVisible, setModifyOrderVisible] = useState(false);

  return (
    <>
      <ModifyChargeModel
        {...order}
        visible={modifyOrderVisible}
        setVisible={setModifyOrderVisible}
        setUpdate={() => {
          setUpdate(update => !update);
        }}
      />
      <CancelChargeModel
        visible={cancelOrderVisible}
        setVisible={setCancelOrderVisible}
      />

      <Back title="查看当前预约" />
      <Card
        actions={[
          <Button
            key="modify"
            type="primary"
            onClick={() => setModifyOrderVisible(true)}
          >
            修改订单
          </Button>,
          <Button
            key="remove"
            type="primary"
            danger
            onClick={() => setCancelOrderVisible(true)}
          >
            取消订单
          </Button>,
        ]}
      >
        {order ? (
          <Descriptions title="预约信息">
            <Descriptions.Item label="充电类别">
              {{ F: "快充", T: "慢充" }[order.chargeType]}
            </Descriptions.Item>
            <Descriptions.Item label="充电量">
              {order.chargeQuantity}度（kWH）
            </Descriptions.Item>
            <Descriptions.Item label="排号">{lineNo}</Descriptions.Item>
            <Descriptions.Item label="排名">
              {rank ? `您排在等待区第${rank}位` : "正在充电区"}
            </Descriptions.Item>
            <Descriptions.Item label="预计完成充电时间">
              {endingTime === -1
                ? "当前无法预估，请耐心等待"
                : new Date(endingTime).toLocaleString()}
            </Descriptions.Item>
          </Descriptions>
        ) : (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />
        )}
      </Card>
    </>
  );
}

export default OrderInfo;
