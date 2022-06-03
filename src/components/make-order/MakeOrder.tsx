import { Button, Card, Form, InputNumber, message, Radio } from "antd";
import React from "react";
import { useNavigate } from "react-router-dom";
import { post } from "../../utils";
import Back from "../back/Back";
import "./MakeOrder.css";

function Order() {
  const navigate = useNavigate();
  const key = "loading";

  function onFinish(values: {
    chargeQuantity: number;
    chargeType: "fast" | "slow";
  }) {
    message.loading({ content: "处理中...", duration: 0, key });
    post("userSendOrder", values)
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
              <Radio value="fast">快充</Radio>
              <Radio value="slow">慢充</Radio>
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
