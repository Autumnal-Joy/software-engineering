import { BackTop, Card, Collapse, Descriptions, List, message } from "antd";
import React, { useEffect, useState } from "react";
import { post } from "../../utils";
import Back from "../back/Back";
import "./Table.css";

type TableData = {
  time: string;
  totalChargeCount: number;
  totalChargeTime: number;
  totalChargeQuantity: number;
  totalChargeCost: number;
  totalServiceCost: number;
  totalCost: number;
  chargers: {
    chargerID: number;
    totalChargeCount: number;
    totalChargeTime: number;
    totalChargeQuantity: number;
    totalChargeCost: number;
    totalServiceCost: number;
    totalCost: number;
  }[];
}[];

interface TableDataRes {
  message: string;
  data: TableData;
}

function Table() {
  const [tableData, setTableData] = useState<TableData>();
  useEffect(() => {
    post<TableDataRes>("adminGetTable", {})
      .then(res => {
        setTableData(res.data);
      })
      .catch(e => {
        message.error({ content: e.message, key: "adminGetChargers" });
      });
  }, []);

  return (
    <>
      <BackTop />
      <Back title="查看报表" />
      <List
        dataSource={tableData}
        itemLayout="vertical"
        renderItem={item => (
          <List.Item key={item.time}>
            <Card bordered={false}>
              <Descriptions title={item.time} size="small">
                <Descriptions.Item label="总计充电时长">
                  {item.totalChargeTime}
                </Descriptions.Item>
                <Descriptions.Item label="总计充电次数">
                  {item.totalChargeCount}
                </Descriptions.Item>
                <Descriptions.Item label="总计充电电量">
                  {item.totalChargeQuantity}
                </Descriptions.Item>
                <Descriptions.Item label="总计充电费用">
                  {item.totalChargeCost}
                </Descriptions.Item>
                <Descriptions.Item label="总计服务费用">
                  {item.totalServiceCost}
                </Descriptions.Item>
                <Descriptions.Item label="总计费用">
                  {item.totalCost}
                </Descriptions.Item>
              </Descriptions>
            </Card>
            <Collapse ghost>
              {item.chargers.map(item => (
                <Collapse.Panel
                  header={`充电桩#${item.chargerID}`}
                  key={item.chargerID}
                >
                  <Card bordered={false}>
                    <Descriptions size="small">
                      <Descriptions.Item label="总计充电时长">
                        {item.totalChargeTime}
                      </Descriptions.Item>
                      <Descriptions.Item label="总计充电次数">
                        {item.totalChargeCount}
                      </Descriptions.Item>
                      <Descriptions.Item label="总计充电电量">
                        {item.totalChargeQuantity}
                      </Descriptions.Item>
                      <Descriptions.Item label="总计充电费用">
                        {item.totalChargeCost}
                      </Descriptions.Item>
                      <Descriptions.Item label="总计服务费用">
                        {item.totalServiceCost}
                      </Descriptions.Item>
                      <Descriptions.Item label="总计费用">
                        {item.totalCost}
                      </Descriptions.Item>
                    </Descriptions>
                  </Card>
                </Collapse.Panel>
              ))}
            </Collapse>
          </List.Item>
        )}
      />
    </>
  );
}

export default Table;
