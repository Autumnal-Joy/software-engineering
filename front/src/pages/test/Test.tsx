import { Button, Card, Form, Input, message, InputNumber } from "antd";
import CryptoJS from "crypto-js";
import React, { useEffect, useState } from "react";
import Back from "../../components/back/Back";
import { post } from "../../utils/net";
import "./Test.css";

const { TextArea } = Input;

function Test() {
  const [timer, setTimer] = useState<ReturnType<typeof setInterval>>();

  useEffect(() => {
    return () => clearInterval(timer);
  }, [timer]);

  const onFinish = (values: { moment: number; text: string }) => {
    const events = values.text
      .split("\n")
      .filter((s: string) => s)
      .map((s: string) => s.replace(/ /g, ""))
      .map((s: string) => s.replace(/\(/g, ""))
      .map((s: string) => s.replace(/\)/g, ""))
      .map((s: string) => s.split(","));
    const iter = events.entries();

    const timer = setInterval(() => {
      const { value, done } = iter.next();
      if (done) {
        clearInterval(timer);
      } else {
        const [index, event] = value;
        const [eventType, id, chargeType, number] = event;
        message.info(`事件${index}：(${event.join(",")})`);

        if (eventType === "A") {
          handleApply(id, chargeType, Number(number));
        } else if (eventType === "B") {
          handleBreakdown(id, chargeType, Boolean(+number));
        } else {
          handleChange(id, chargeType, Number(number));
        }
      }
    }, values.moment);
    setTimer(timer);
  };

  function handleApply(
    username: string,
    chargeType: string,
    chargeQuantity: number
  ) {
    message.loading({ content: "处理中...", duration: 0, key: "A" });
    if (chargeType != "O") {
      post("userSendOrder", {
        username,
        password: CryptoJS.MD5("123456").toString(),
        chargeType,
        chargeQuantity,
      })
        .then(() => {
          message.success({ content: "预约成功", key: "A" });
        })
        .catch(e => {
          message.error({ content: e.message, key: "A" });
        });
    } else {
      post("userSendCancelCharge", {
        username,
        password: CryptoJS.MD5("123456").toString(),
      })
        .then(() => {
          message.success({ content: "取消成功", key: "A" });
        })
        .catch(e => {
          message.error({ content: e, key: "A" });
        });
    }
  }

  function handleBreakdown(
    chargerID: string,
    _chargeType: string,
    turn: boolean
  ) {
    message.loading({ content: "处理中...", duration: 0, key: "B" });

    post("adminTurnCharger", {
      username: "admin",
      password: CryptoJS.MD5("123456").toString(),
      chargerID,
      turn: turn ? "on" : "off",
    })
      .then(() => {
        message.success({ content: turn ? "开启成功" : "关闭成果", key: "B" });
      })
      .catch(e => {
        message.error({ content: e.message, key: "B" });
      });
  }

  function handleChange(
    username: string,
    chargeType: string,
    chargeQuantity: number
  ) {
    message.loading({ content: "处理中...", duration: 0, key: "C" });
    post<{
      message: string;
      data: {
        chargeType: "F" | "T";
        chargeQuantity: number;
      };
    }>("userGetOrder", {
      username,
      password: CryptoJS.MD5("123456").toString(),
    })
      .then(({ data }) => {
        if (chargeQuantity == -1) {
          chargeQuantity = data.chargeQuantity;
        }
        let promise;
        if (chargeType != "O") {
          promise = post("userSendChargeType", {
            username,
            password: CryptoJS.MD5("123456").toString(),
            chargeType,
            chargeQuantity,
          });
        } else {
          promise = post("userSendChargeQuantity", {
            username,
            password: CryptoJS.MD5("123456").toString(),
            chargeQuantity,
          });
        }
        promise
          .then(() => {
            message.success({ content: "修改成功", key: "C" });
          })
          .catch(e => {
            message.error({ content: e.message, key: "C" });
          });
      })
      .catch(e => {
        message.error({ content: e.message, key: "userGetOrder" });
      });
  }

  return (
    <>
      <Back title="验收测试" />
      <Card>
        <Form onFinish={onFinish}>
          <Form.Item
            label="间隔时间"
            name="moment"
            initialValue={30_000}
            rules={[
              {
                required: true,
                message: "间隔时间不能为空",
              },
            ]}
          >
            <InputNumber min={100} max={30_000} addonAfter="毫秒" />
          </Form.Item>
          <Form.Item
            label="验收测试数据"
            name="text"
            rules={[
              {
                required: true,
                message: "测试数据不能为空",
              },
              {
                transform: value =>
                  value
                    .split("\n")
                    .filter((s: string) => s)
                    .map((s: string) => s.replace(/ /g, "")),
                validator: (_, value: string[]) => {
                  const pattern =
                    /^(?:(?:\([AC],V\d+,[FTO],[+-]?\d+(?:\.\d+)?\))|(?:\(B,[FT]\d+,O,[01]\)))$/;
                  if (value.every(text => pattern.test(text))) {
                    return Promise.resolve();
                  } else {
                    return Promise.reject(new Error("格式错误"));
                  }
                },
              },
            ]}
          >
            <TextArea rows={15} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              开始定时
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </>
  );
}

export default Test;
