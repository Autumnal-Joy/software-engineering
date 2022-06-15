import { Button, Card, Form, InputNumber, message, Radio } from "antd";
import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../components/UserManager";
import { post } from "../../utils/net";
import Back from "../../components/back/Back";
import "./MakeOrder.css";

function Order() {
  const key = "loading";

  const navigate = useNavigate();
  const auth = useAuth();
  const { username, password } = auth.userAuth;

  function onFinish(values: { chargeQuantity: number; chargeType: "F" | "T" }) {
    message.loading({ content: "处理中...", duration: 0, key });
    post("userSendOrder", { username, password, ...values })
      .then(() => {
        message.success({ content: "预约成功", key });
        navigate(-1);
      })
      .catch(e => {
        message.error({ content: e.message, key });
      });
  }

  return (
    <>
      <Back title="发起排号申请" />
      <Card>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item
            label="充电类别"
            name="chargeType"
            rules={[{ required: true, message: "请选择充电类别" }]}
          >
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

export default Order;
