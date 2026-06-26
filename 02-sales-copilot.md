# Case 2 - Sales Chat Copilot: Tóm tắt hội thoại và tra cứu theo tín hiệu khách gửi

## Mục tiêu

Case này đại diện cho một kiểu AI rất hay gặp ở thị trường Việt Nam:

- đội sales hoặc chăm sóc khách hàng đang nhắn tin với khách qua Zalo, Facebook, live chat hoặc CRM inbox,
- AI không thay người chốt đơn hoàn toàn,
- nhưng AI có thể đọc hội thoại, tóm tắt ngữ cảnh, phát hiện tín hiệu như số điện thoại / email / mã đơn / mã khách,
- rồi tra cứu hệ thống nội bộ để đưa thông tin cần thiết cho nhân viên xử lý nhanh hơn.

Điểm khó của case này là:

- có nhiều logic lookup tự động,
- có nguy cơ match sai người hoặc sai đơn,
- có dữ liệu nhạy cảm,
- và rất dễ “trông thông minh” dù thực tế đang suy luận sai.

Chỉ cần thiết kế eval ban đầu, không cần code full system.

---

## 1. Bối cảnh

Một doanh nghiệp bán hàng online tại Việt Nam có đội sales / chăm sóc khách hàng xử lý tin nhắn từ nhiều kênh:

- Zalo OA,
- Facebook Messenger,
- web chat,
- CRM inbox nội bộ.

Khi khách nhắn tin, nhân viên thường phải làm nhiều việc thủ công:

- đọc lại lịch sử hội thoại,
- hiểu khách đang hỏi về vấn đề gì,
- tự tìm số điện thoại / email / mã đơn trong đoạn chat,
- tra CRM hoặc hệ thống đơn hàng,
- rồi mới biết khách này là ai, đang ở trạng thái nào, đơn hàng nào liên quan và nên trả lời tiếp ra sao.

Nhóm muốn thêm một **Sales Chat Copilot** để:

- tóm tắt cuộc hội thoại hiện tại,
- phát hiện các mã hoặc thông tin nhận diện khách,
- tra cứu nhanh hồ sơ khách / đơn hàng / ticket cũ,
- gợi ý thông tin quan trọng cho nhân viên,
- và có thể gợi ý câu trả lời nháp.

AI **không được tự gửi tin nhắn**, **không được tự chốt đơn**, và **không được tự sửa dữ liệu khách**.

---

## 2. Workflow logic tham khảo (ASCII)

```text
Khách nhắn tin đến từ Zalo / Facebook / web chat
    ↓
AI đọc:
- tin nhắn mới nhất
- lịch sử hội thoại gần đây
- metadata kênh nhắn tin
    ↓
AI phát hiện tín hiệu:
- số điện thoại
- email
- mã đơn
- mã khách
- tên sản phẩm / nhu cầu mua
    ↓
Nếu có tín hiệu đủ mạnh
    ↓
Tra CRM / OMS / ticket history
    ↓
Hiển thị cho nhân viên:
- tóm tắt hội thoại
- khách đang hỏi gì
- hồ sơ / đơn hàng liên quan
- cảnh báo nếu có điểm mâu thuẫn
- gợi ý bước tiếp theo
    ↓
Nhân viên xem lại và quyết định:
- trả lời thủ công
- dùng nháp AI rồi sửa
- hỏi thêm khách
- chuyển sale khác / chuyển CSKH / escalate
```

---

## 3. Khung UI gợi ý (ASCII)

```text
+------------------------------------------------------------------------------------------------+
| Hộp chat khách hàng                                                                            |
+------------------------------------------------------------------------------------------------+
| Kênh: Zalo OA                               Khách: Chưa xác định chắc chắn                      |
|-----------------------------------------------------------------------------------------------|
| Khách: Chị kiểm tra giúp em đơn này với, em gửi số 0909123456                                  |
| Khách: Mã đơn hình như là DH-48291                                                             |
| NV sale: ...                                                                                   |
|-----------------------------------------------------------------------------------------------|
| Copilot                                                                                       |
| - Tóm tắt hội thoại: [ ................................................................. ]    |
| - Tín hiệu phát hiện: [ số điện thoại ] [ mã đơn ]                                            |
| - Khách / đơn liên quan: [ ? ]                                                                 |
| - Cảnh báo: [ Có / Không ]                                                                     |
| - Gợi ý bước tiếp theo: [ ............................................................... ]    |
|-----------------------------------------------------------------------------------------------|
| [Xem hồ sơ] [Xem đơn hàng] [Dùng nháp AI] [Hỏi thêm khách] [Chuyển người xử lý]              |
+------------------------------------------------------------------------------------------------+
```

Học viên có thể dùng khung này hoặc chỉnh lại nếu thấy logic sản phẩm cần thay đổi. Điểm quan trọng là phải tự đề xuất output contract tối thiểu phía sau để màn hình này hiển thị được.

---

## 4. Tình huống mẫu

### Tình huống A - Khách gửi số điện thoại

```text
Khách: Chị check giúp em đơn cũ với, số em là 0909123456.
```

### Tình huống B - Khách gửi email

```text
Khách: Bên mình kiểm tra lại giúp mình email linh.nguyen@abc.vn nhé, hôm trước có tư vấn mà chưa thấy báo giá.
```

### Tình huống C - Khách gửi mã đơn

```text
Khách: Em hỏi đơn DH-48291 đang tới đâu rồi ạ?
```

### Tình huống D - Khách hỏi mơ hồ

```text
Khách: Chị ơi bên em xử lý giúp case này với, gấp lắm.
```

---

## 5. Business rules / operational rules

- AI có thể **đề xuất tra cứu** hoặc **tự động tra cứu nội bộ** nếu tín hiệu nhận diện đủ rõ, nhưng không được tự gửi phản hồi cho khách.
- Nếu có nhiều bản ghi cùng khớp với một số điện thoại / email / mã, AI không được tự chốt một bản ghi duy nhất.
- Nếu không tìm thấy hồ sơ phù hợp, AI phải nói rõ là “chưa tìm thấy”, không được bịa ra khách hoặc đơn.
- Nếu khách gửi dữ liệu nhạy cảm, hệ thống chỉ hiển thị phần cần thiết cho nhân viên, không bung toàn bộ dữ liệu không liên quan.
- Nếu kết quả CRM và kết quả đơn hàng mâu thuẫn, AI phải cảnh báo mức độ không chắc chắn.
- AI có thể gợi ý nháp trả lời, nhưng bản nháp phải được nhân viên xem lại trước khi gửi.
- AI không được tự tạo đơn mới chỉ vì phát hiện nhu cầu mua, trừ khi luồng đó được người dùng nội bộ xác nhận rõ.

---

## 6. Ví dụ full luồng để hình dung nhanh

### Tình huống

Khách nhắn vào Zalo OA:

```text
Chị kiểm tra giúp em đơn DH-48291 với ạ.
Số em là 0909123456.
Hôm trước chị tư vấn cho em máy lọc nước rồi.
```

### Data mẫu

**Dữ liệu từ CRM**

- Tên khách: `Nguyễn Minh Linh`
- Số điện thoại: `0909123456`
- Kênh lead: `Zalo OA`
- Sales owner: `Trâm`
- Trạng thái lead: `Đã mua lần 1`

**Dữ liệu từ OMS**

- Mã đơn: `DH-48291`
- Sản phẩm: `Máy lọc nước RO Mini`
- Trạng thái: `Đang giao`
- Dự kiến giao: `Hôm nay`

**Lịch sử hội thoại gần đây**

- Khách từng hỏi báo giá
- Sales đã tư vấn 2 model
- Khách đã chốt 1 model hôm trước

### Workflow ASCII

```text
Khách gửi mã đơn + số điện thoại
    ↓
AI phát hiện 2 tín hiệu tra cứu:
- mã đơn
- số điện thoại
    ↓
AI tra CRM + OMS
    ↓
Hệ thống nối thông tin:
- đây là khách cũ
- đơn DH-48291 đang giao
- sales owner hiện tại là Trâm
    ↓
Copilot hiển thị:
- tóm tắt hội thoại
- hồ sơ khách
- trạng thái đơn
- gợi ý bước tiếp theo
    ↓
Nhân viên sales đọc lại
    ↓
Nhân viên chọn:
- dùng nháp AI rồi sửa
- xem đơn chi tiết
- hỏi thêm khách
```

### UI trước khi AI xử lý (ASCII)

```text
+------------------------------------------------------------------------------------------------+
| Hộp chat khách hàng                                                                            |
+------------------------------------------------------------------------------------------------+
| Kênh: Zalo OA                                                                                  |
|-----------------------------------------------------------------------------------------------|
| Khách: Chị kiểm tra giúp em đơn DH-48291 với ạ.                                               |
| Khách: Số em là 0909123456.                                                                    |
|-----------------------------------------------------------------------------------------------|
| Copilot: Chưa phân tích                                                                        |
+------------------------------------------------------------------------------------------------+
```

### UI sau khi AI xử lý (ASCII)

```text
+------------------------------------------------------------------------------------------------+
| Hộp chat khách hàng                                                                            |
+------------------------------------------------------------------------------------------------+
| Kênh: Zalo OA                               Sales owner hiện tại: Trâm                         |
|-----------------------------------------------------------------------------------------------|
| Khách: Chị kiểm tra giúp em đơn DH-48291 với ạ.                                               |
| Khách: Số em là 0909123456.                                                                    |
|-----------------------------------------------------------------------------------------------|
| Copilot                                                                                       |
| - Tóm tắt hội thoại: Khách cũ đang hỏi về tình trạng đơn vừa mua.                             |
| - Tín hiệu phát hiện: [0909123456] [DH-48291]                                                  |
| - Hồ sơ khách: Nguyễn Minh Linh - Đã mua lần 1                                                 |
| - Đơn hàng: Máy lọc nước RO Mini - Trạng thái: Đang giao                                       |
| - Gợi ý: Báo khách đơn đang giao hôm nay và xác nhận khung giờ nhận hàng.                     |
| - Nháp trả lời: "Dạ em thấy đơn DH-48291 đang được giao hôm nay..."                            |
|-----------------------------------------------------------------------------------------------|
| [Xem CRM] [Xem đơn] [Dùng nháp AI] [Hỏi thêm khách]                                           |
+------------------------------------------------------------------------------------------------+
```

Ví dụ này giúp người đọc hình dung ngay:

- AI đang tự động bắt tín hiệu gì,
- lookup nào đang diễn ra ở hậu trường,
- thông tin nào được kéo ra cho sales,
- và ranh giới giữa “gợi ý” với “tự hành động”.

---

## 7. Seed cases

Đây không phải full dataset. Đây chỉ là các seed cases để học viên hình dung phạm vi và failure modes.

### Seed A - Match rõ, một bản ghi duy nhất

- Khách gửi đúng số điện thoại.
- CRM trả về đúng một hồ sơ.
- Có một đơn hàng gần nhất đang giao.
- Kỳ vọng: AI tóm tắt đúng và hiển thị đúng đơn liên quan.

### Seed B - Một tín hiệu khớp nhiều bản ghi

- Cùng một số điện thoại gắn với hai hồ sơ do nhập trùng.
- Kỳ vọng: AI phải cảnh báo mơ hồ và yêu cầu nhân viên chọn đúng hồ sơ.

### Seed C - Khách gửi mã đơn hợp lệ nhưng không phải khách hiện tại

- Mã đơn tồn tại trong hệ thống nhưng thuộc người khác.
- Kỳ vọng: AI không được suy ra đây chắc chắn là đơn của người đang chat.

### Seed D - Khách hỏi mơ hồ, chưa có tín hiệu tra cứu

- Kỳ vọng: AI không nên bịa hồ sơ; nên gợi ý hỏi thêm số điện thoại / email / mã đơn.

### Seed E - Dữ liệu hệ thống mâu thuẫn

- CRM nói khách đang là lead mới.
- OMS lại có lịch sử đơn cũ.
- Kỳ vọng: AI phải nêu rõ điểm mâu thuẫn thay vì tóm tắt như thể mọi thứ đã chắc chắn.

---

## 8. Mock outcome để soi

Giả sử trên UI nội bộ, Copilot hiển thị như sau sau khi khách gửi:

```text
Khách: Chị kiểm tra giúp em đơn này với, em gửi số 0909123456. Mã đơn DH-48291.
```

```text
+------------------------------------------------------------------------------------------------+
| Copilot                                                                                        |
+------------------------------------------------------------------------------------------------+
| Tóm tắt hội thoại: Khách hỏi về tình trạng đơn hàng cũ.                                        |
| Tín hiệu phát hiện: 0909123456, DH-48291                                                       |
| Khách liên quan: Nguyễn Minh Linh                                                              |
| Đơn liên quan: DH-48291 - Đã giao thành công                                                   |
| Cảnh báo: Không                                                                                |
| Gợi ý cho sales: Báo khách đơn đã giao và mời mua thêm sản phẩm mới.                           |
+------------------------------------------------------------------------------------------------+
```

Kết quả này có thể trông “mượt”, nhưng vẫn có khả năng rất nguy hiểm nếu:

- số điện thoại khớp nhiều người,
- mã đơn thuộc khách khác,
- trạng thái “đã giao” là dữ liệu cũ,
- hoặc AI đang đẩy sales upsell sai thời điểm.

---

## 9. Bộ test gợi ý v0

Phần này chỉ để gợi ý cách nghĩ coverage từ bài hôm trước. Không phải deliverable bắt buộc.

Bạn có thể dùng 8 tình huống dưới đây để nghĩ coverage ban đầu:

| ID | Tình huống | Điều cần bắt |
| --- | --- | --- |
| SC-01 | Khách gửi số điện thoại đúng format, match 1 hồ sơ | lookup đúng |
| SC-02 | Khách gửi email viết hoa/thường lẫn lộn | normalization |
| SC-03 | Khách gửi mã đơn sai 1 ký tự | không tự match bừa |
| SC-04 | Cùng số điện thoại khớp 2 hồ sơ | ambiguity handling |
| SC-05 | Khách chỉ nói “chị kiểm tra giúp em case này” | ask for missing info |
| SC-06 | CRM và OMS mâu thuẫn | uncertainty + warning |
| SC-07 | AI gợi ý nháp trả lời nhưng nhầm intent bán hàng thành hậu mãi | summary / intent error |
| SC-08 | Khách gửi tiếng Việt không dấu + mã đơn | robustness với ngôn ngữ thực tế |

---

## 10. Bạn phải đề xuất thêm 5 Dataset Edge Cases

Sau khi đọc bộ test gợi ý v0 ở trên, hãy đề xuất thêm 5 case cần đưa vào reference dataset version đầu.

Không cần nộp một bảng coverage riêng. Hãy chọn 5 case đại diện cho các lát cắt khác nhau, ví dụ: match rõ, thiếu tín hiệu, ambiguity, dữ liệu mâu thuẫn, và action safety.

1. Happy path:
2. Ambiguous lookup:
3. Missing information:
4. Conflicting systems:
5. Regression case:

Với mỗi case, thêm 1 dòng ngắn giải thích:

- case này dùng để bắt failure gì?

---

## 11. Nhiệm vụ học viên

Hãy điền workbook bên dưới cho case này.

Không cần:

- viết connector CRM thật,
- viết regex hoặc parser thật,
- làm lại `User Input Grid` hay `Scenario Dataset v0/v1`,
- code full workflow,
- dựng UI đẹp.

Cần làm:

- xác định unit of AI work đủ nhỏ,
- viết quality question cho lát cắt này,
- đề xuất output contract tối thiểu,
- quyết định phần nào chấm bằng code / LLM / human,
- đặt release gate cho hành vi tra cứu và hiển thị gợi ý,
- đề xuất edge cases cho dataset,
- và lập pilot plan có thời gian + chi phí sơ bộ.

---

## 12. Bạn nên làm gì ở case 2?

Đây là case scaffold trung bình, nên bạn không cần giữ nguyên workflow và UI gợi ý.

Nên làm theo thứ tự:

1. Dùng workflow tham khảo để xác định các bước chính của hệ thống.
2. Quyết định chỗ nào AI được tự lookup, chỗ nào phải hỏi thêm.
3. Xem lại khung UI và chỉnh nếu bạn thấy thiếu checkpoint quan trọng.
4. Chỉ sau đó mới chốt output contract và release gate.

Case này thường thiên về **ops / sales / CRM** hơn là domain chuyên môn sâu. Nếu chọn **không cần domain expert**, bạn vẫn phải giải thích rõ vì sao chỉ cần human review từ team vận hành là đủ.

---

## 13. Workbook

### 1. Unit of Work

> Tôi chọn lát cắt công việc (Unit of Work) là: **Từ một đoạn hội thoại đầu vào, AI thực hiện một chuỗi công việc bao gồm phát hiện tín hiệu nhận diện (số điện thoại, mã đơn), tự động tra cứu các hệ thống liên quan (CRM, OMS), và cuối cùng tạo ra một bản tóm tắt cùng gợi ý hành động cho nhân viên sales.**
>
> Đây là một đơn vị công việc đủ nhỏ để đánh giá vì nó có đầu vào (hội thoại) và đầu ra (bộ gợi ý) rất cụ thể, cho phép kiểm thử độc lập từng trường hợp. Tuy nhiên, nó vẫn chứa đựng rủi ro vận hành nghiêm trọng: nếu AI tra cứu sai hồ sơ khách hàng hoặc đơn hàng, nó có thể làm lộ thông tin sai lệch, khiến nhân viên sales tư vấn nhầm, gây mất lòng tin của khách hàng và ảnh hưởng trực tiếp đến doanh thu.

### 2. Quality Question

> **Câu hỏi chất lượng của tôi là: Với một tín hiệu đầu vào, Copilot có tra cứu đúng hồ sơ khách hàng và đơn hàng liên quan không, và quan trọng hơn, nó có biết dừng lại và cảnh báo một cách rõ ràng khi phát hiện dữ liệu mâu thuẫn (giữa các hệ thống) hoặc mơ hồ (nhiều hồ sơ trùng khớp) để ngăn nhân viên sales đưa ra thông tin sai lệch không?**

> Câu hỏi này là trọng tâm vì nếu Copilot thất bại, nó có thể tự tin hiển thị hồ sơ của khách hàng A cho nhân viên đang nói chuyện với khách hàng B. Nhân viên, vì tin tưởng vào AI, có thể đưa ra thông tin sai hoàn toàn ("đơn hàng của anh đã giao rồi ạ" trong khi đó là đơn của người khác), dẫn đến mất lòng tin của khách hàng, rủi ro lộ thông tin và khiến chính nhân viên không còn tin vào công cụ nữa.

### 3. Output Contract tối thiểu

> Dưới đây là các trường tối thiểu mà tôi đề xuất cho Output Contract:
>
> - **`summary` (string):**
>   - **Lý do:** Cần thiết để hiển thị `Tóm tắt hội thoại` trên UI, giúp nhân viên sales nắm bắt nhanh ngữ cảnh. Chất lượng (súc tích, không bịa đặt) là một tiêu chí eval quan trọng, thường được chấm bằng LLM.
> - **`detected_signals` (array of objects):**
>   - **Lý do:** Hiển thị các `Tín hiệu phát hiện` trên UI (ví dụ: `[số điện thoại]`). Trường này cực kỳ quan trọng cho việc eval và debug, giúp xác minh AI đã hành động dựa trên đúng thông tin đầu vào.
> - **`lookup_status` (enum):**
>   - **Lý do:** Một trường backend để kiểm soát logic. Các giá trị có thể là `SUCCESS_SINGLE_MATCH`, `AMBIGUOUS_MULTIPLE_MATCHES`, `NOT_FOUND`, `CONFLICT`. Nó quyết định việc có hiển thị `Cảnh báo` trên UI hay không và là một mục tiêu chính cho việc kiểm tra tự động bằng code (eval).
> - **`lookup_results` (array of objects):**
>   - **Lý do:** Chứa dữ liệu thực tế được tra cứu từ CRM/OMS để hiển thị `Khách / đơn liên quan` trên UI. Tính chính xác của dữ liệu này (có đúng là của khách hàng không) là một trong những điểm eval quan trọng nhất.
> - **`warnings` (array of strings):**
>   - **Lý do:** Hiển thị trực tiếp các cảnh báo trên UI. Trường này được sinh ra từ `lookup_status` (ví dụ: `AMBIGUOUS_MULTIPLE_MATCHES` -> `warnings: ["Tìm thấy nhiều hồ sơ khớp"]`). Đây là một cổng an toàn (safety gate) cốt lõi và là mục tiêu eval bắt buộc.
> - **`suggested_next_step` (string):**
>   - **Lý do:** Hiển thị `Gợi ý bước tiếp theo` trên UI để hướng dẫn nhân viên sales. Mức độ hữu ích và an toàn của gợi ý này là một tiêu chí eval quan trọng (ví dụ: không gợi ý upsell sai thời điểm).
> - **`suggested_reply` (string, optional):**
>   - **Lý do:** Cung cấp `Nháp trả lời` trên UI. Đây là một hành động có rủi ro cao hơn, do đó chất lượng, giọng văn và tính chính xác của nó phải được eval rất kỹ, thường là bởi con người (human review).

### 4. Eval Decision Map

| Thành phần cần chấm | Code | LLM | Human | Expert | Lý do |
| --- | :---: | :---: | :---: | :---: | --- |
| **1. Tuân thủ schema và enum** (`lookup_status`) | ✅ | | | | **Code** là cách nhanh, rẻ và đáng tin cậy nhất để kiểm tra xem output có đúng định dạng JSON và các giá trị có nằm trong danh sách cho phép không (ví dụ: `lookup_status` phải là `SUCCESS_SINGLE_MATCH`). |
| **2. Xử lý trạng thái tra cứu** (`lookup_status` -> `warnings`) | ✅ | | | | **Code** có thể kiểm tra các quy tắc cứng, ví dụ: nếu `lookup_status` là `AMBIGUOUS_MULTIPLE_MATCHES` thì trường `warnings` không được rỗng. Đây là một cổng an toàn (safety gate) quan trọng. |
| **3. Độ chính xác của việc tra cứu** (`lookup_results`) | | | ✅ | | Đây là rủi ro vận hành lớn nhất. Chỉ có **Human** (Sales Ops, Senior Sales) mới có thể xác nhận xem hồ sơ khách hàng/đơn hàng mà AI tra cứu được có thực sự là của người đang chat hay không, bằng cách đối chiếu với ngữ cảnh hội thoại. |
| **4. Chất lượng của tóm tắt** (`summary`) | | ✅ | ✅ | | **LLM** rất phù hợp để đánh giá ở quy mô lớn xem tóm tắt có súc tích, trung thực (không bịa đặt) và nắm bắt đúng ý chính không. **Human** cần thiết để tạo bộ dữ liệu vàng và kiểm định (calibrate) LLM judge. |
| **5. Mức độ hữu ích của gợi ý** (`suggested_next_step`) | | ✅ | ✅ | | Việc một gợi ý có "hữu ích" và "an toàn" hay không (ví dụ: không mời mua thêm khi khách đang phàn nàn) đòi hỏi sự hiểu biết ngữ nghĩa. **LLM** có thể chấm, nhưng **Human** phải định nghĩa rubric và review các ca nhạy cảm. |
| **6. Chất lượng của nháp trả lời** (`suggested_reply`) | | | ✅ | | Vì đây là nội dung có thể được gửi trực tiếp cho khách, rủi ro rất cao. **Human** phải review kỹ lưỡng về giọng văn, tính chính xác và sự phù hợp với tình huống, đặc biệt là ở giai đoạn đầu. |

### 5. Kiểm tra tự động bằng code

- **Kiểm tra:** Output phải là một JSON hợp lệ và tuân thủ đúng schema đã định nghĩa (ví dụ: có đủ các trường `summary`, `lookup_status`, `lookup_results`).
  **Vì sao nên giao cho code:** Đây là kiểm tra cấu trúc cơ bản nhất. Code có thể xác thực schema một cách nhanh chóng, rẻ và đáng tin cậy. Bất kỳ lỗi nào ở bước này đều cho thấy AI đã thất bại ở mức độ cơ bản nhất và có thể làm sập các hệ thống tích hợp phía sau.

- **Kiểm tra:** Giá trị của trường `lookup_status` phải nằm trong một danh sách các giá trị cho phép (enum), ví dụ: `SUCCESS_SINGLE_MATCH`, `AMBIGUOUS_MULTIPLE_MATCHES`, `NOT_FOUND`, `CONFLICT`.
  **Vì sao nên giao cho code:** Việc kiểm tra một giá trị có thuộc một tập hợp cố định hay không là một logic xác định (deterministic). Giao cho code đảm bảo AI không "bịa" ra một trạng thái mới, gây lỗi cho logic hiển thị và các cổng an toàn.

- **Kiểm tra:** Nếu `lookup_status` là `AMBIGUOUS_MULTIPLE_MATCHES` hoặc `CONFLICT`, thì trường `warnings` không được rỗng.
  **Vì sao nên giao cho code:** Đây là một quy tắc nghiệp vụ cứng và là một cổng an toàn (safety gate) cốt lõi. Code có thể kiểm tra điều kiện này một cách chính xác tuyệt đối, đảm bảo hệ thống luôn cảnh báo cho nhân viên trong các tình huống mơ hồ, ngăn ngừa việc tư vấn sai khách hàng.

- **Kiểm tra:** Nếu `lookup_status` là `NOT_FOUND`, thì trường `lookup_results` phải là một mảng rỗng.
  **Vì sao nên giao cho code:** Đây là một kiểm tra logic nhất quán. Code có thể dễ dàng xác nhận rằng khi không tìm thấy kết quả, hệ thống không vô tình trả về dữ liệu rác hoặc dữ liệu từ một lần tra cứu trước đó.

- **Kiểm tra:** Nếu `lookup_status` là `SUCCESS_SINGLE_MATCH`, thì trường `lookup_results` phải chứa chính xác một phần tử.
  **Vì sao nên giao cho code:** Đây là một kiểm tra tính nhất quán của dữ liệu. Code có thể đếm số phần tử trong mảng một cách chính xác để đảm bảo logic "khớp một bản ghi duy nhất" được tuân thủ.

- **Kiểm tra:** Các thực thể trong `detected_signals` (ví dụ: số điện thoại, mã đơn) phải thực sự tồn tại trong đoạn hội thoại đầu vào.
  **Vì sao nên giao cho code:** Đây là một kiểm tra tính trung thực (groundedness) ở mức độ cơ bản. Việc tìm kiếm một chuỗi con trong một chuỗi lớn là tác vụ xác định của code, giúp phát hiện các trường hợp AI "ảo giác" ra tín hiệu không có thật.

- **Kiểm tra:** Trường `summary` không được rỗng hoặc chỉ chứa khoảng trắng.
  **Vì sao nên giao cho code:** Việc kiểm tra một chuỗi có rỗng hay không là việc cơ bản của code. Rule này đảm bảo AI luôn cung cấp một tóm tắt, dù chất lượng của nó sẽ được chấm bằng các phương pháp khác.

- **Kiểm tra:** Nếu `lookup_status` không phải là `SUCCESS_SINGLE_MATCH`, thì `suggested_reply` (nếu có) không được chứa thông tin cá nhân nhạy cảm (ví dụ: "Chào anh Minh,").
  **Vì sao nên giao cho code:** Code có thể dùng regex hoặc các quy tắc đơn giản để kiểm tra các mẫu câu chào hỏi có chứa tên riêng (lấy từ `lookup_results`) khi chưa xác thực được danh tính. Đây là một lớp phòng vệ để giảm thiểu rủi ro lộ thông tin sai.

### 6. Tiêu chí chấm bằng LLM

- **Tiêu chí:** Chất lượng của `summary` (Tóm tắt hội thoại) có trung thực và chỉ dựa trên thông tin trong hội thoại không (không bịa đặt)?
  **Vì sao code không bắt tốt:** Đây là bài toán kiểm tra tính trung thực (faithfulness/groundedness). Code không thể so sánh ngữ nghĩa giữa tóm tắt và hội thoại gốc để phát hiện thông tin bịa đặt. LLM có thể đọc hiểu cả hai và xác định xem tóm tắt có suy ra những điều không có trong cuộc chat hay không.

- **Tiêu chí:** Chất lượng của `summary` có nắm bắt đúng ý định chính (intent) của khách hàng không?
  **Vì sao code không bắt tốt:** Khách hàng có thể diễn đạt ý định một cách không trực tiếp (ví dụ: "Bên mình có chính sách gì cho khách hàng thân thiết không?" thay vì "Tôi muốn giảm giá"). Code dựa trên từ khóa sẽ bỏ lỡ ý định này, trong khi LLM có thể suy luận được mục đích thực sự đằng sau câu hỏi.

- **Tiêu chí:** Mức độ hữu ích và an toàn của `suggested_next_step` (Gợi ý bước tiếp theo) có phù hợp với ngữ cảnh không?
  **Vì sao code không bắt tốt:** Một gợi ý như "Mời khách mua thêm sản phẩm" có thể hữu ích khi khách đang vui, nhưng lại rất tệ khi khách đang phàn nàn. Việc xác định sự phù hợp này đòi hỏi sự hiểu biết về cảm xúc và tình huống, điều mà code không thể làm được.

- **Tiêu chí:** Chất lượng của `suggested_reply` (Nháp trả lời) có giọng văn phù hợp và giải quyết đúng vấn đề của khách không?
  **Vì sao code không bắt tốt:** Giọng văn (ví dụ: thân thiện, chuyên nghiệp, đồng cảm) là một khái niệm ngữ nghĩa phức tạp. Code không thể đánh giá được một câu trả lời có "đồng cảm" hay không. LLM, được huấn luyện trên dữ liệu hội thoại khổng lồ, có thể đánh giá sắc thái này tốt hơn nhiều.

- **Tiêu chí:** AI có nhận diện đúng các trường hợp cần hỏi thêm thông tin thay vì cố gắng tra cứu với dữ liệu không đầy đủ không?
  **Vì sao code không bắt tốt:** Một tin nhắn như "Kiểm tra giúp mình" không chứa tín hiệu tra cứu rõ ràng. Code sẽ không biết phải làm gì. LLM có thể nhận ra sự thiếu thông tin này và đề xuất hành động là "Hỏi thêm thông tin" thay vì đoán bừa hoặc báo lỗi.

- **Tiêu chí:** AI có phân biệt được giữa thông tin khách hàng cung cấp và thông tin hệ thống tra cứu được khi tóm tắt không?
  **Vì sao code không bắt tốt:** Việc phân biệt nguồn gốc thông tin ("khách nói X", "hệ thống ghi nhận Y") đòi hỏi khả năng suy luận và phân tích nguồn. LLM có thể được huấn luyện để làm rõ điều này trong tóm tắt, giúp nhân viên sales không bị nhầm lẫn giữa hai luồng thông tin.

### 7. Human / Expert Review

> **Người cần review là các Trưởng nhóm Sales (Sales Leads) hoặc nhân viên Vận hành Sales (Sales Ops).** Họ là những người hiểu rõ nhất quy trình bán hàng, cấu trúc dữ liệu trong CRM/OMS, và hậu quả của việc cung cấp thông tin sai cho khách hàng.
>
> **Họ cần tập trung review các rủi ro vận hành sau:**
> 1.  **Lỗi tra cứu sai (Incorrect Lookup):** Các trường hợp AI tự tin trả về một hồ sơ khách hàng (`lookup_status: SUCCESS_SINGLE_MATCH`) nhưng thực tế lại là của người khác. Đây là lỗi nghiêm trọng nhất, có thể dẫn đến lộ thông tin và tư vấn sai.
> 2.  **Lỗi xử lý tình huống mơ hồ (Ambiguity Mismanagement):** Các trường hợp AI không đưa ra cảnh báo (`warnings` rỗng) khi có nhiều hồ sơ trùng khớp hoặc dữ liệu mâu thuẫn.
> 3.  **Lỗi gợi ý hành động (Unsafe Suggestion):** Các trường hợp AI đưa ra gợi ý (`suggested_next_step` hoặc `suggested_reply`) không phù hợp với ngữ cảnh, ví dụ mời mua thêm khi khách đang phàn nàn.
> 4.  **Một mẫu ngẫu nhiên các ca thành công:** Để kiểm tra các lỗi tinh vi hoặc các điểm có thể cải thiện mà không được phát hiện qua các trường hợp lỗi rõ ràng.

Nếu chọn **có domain expert**, bạn phải làm thêm 2 phần dưới đây. Nếu **không cần domain expert**, hãy ghi `Không áp dụng` và giải thích 1 câu.

#### 7A. Màn hình cho Domain Expert (ASCII)

> Không áp dụng. Vì case này không yêu cầu domain expert chuyên sâu (như y tế, pháp lý), vai trò review được đảm nhiệm bởi các Sales Leads/Sales Ops. Do đó, không cần thiết kế một màn hình riêng cho một vai trò không tồn tại trong luồng này.

#### 7B. Tiêu chí review của Domain Expert

> **Không áp dụng.** Vì không cần domain expert, nên cũng không có bộ tiêu chí riêng cho vai trò này. Các tiêu chí đánh giá đã được bao phủ bởi các Sales Leads/Sales Ops trong vai trò human reviewer.

### 8. Release Gate

Một phiên bản Copilot mới sẽ bị **CHẶN (BLOCK)** phát hành nếu vi phạm bất kỳ điều kiện an toàn cốt lõi nào sau đây:

1.  **Không có lỗi tra cứu nghiêm trọng (Zero Critical Lookup Failures):**
    *   **Điều kiện:** `Số lượng lỗi tra cứu sai hồ sơ khách hàng > 0`.
    *   **Lý do:** Việc hiển thị sai hồ sơ khách hàng là một lỗi P0, có thể dẫn đến rò rỉ thông tin cá nhân và tư vấn sai hoàn toàn. Đây là điều kiện chặn tuyệt đối.

2.  **Tỷ lệ phát hiện tình huống mơ hồ (Ambiguity Detection Recall) phải cực cao:**
    *   **Điều kiện:** `Tỷ lệ phát hiện đúng các case cần cảnh báo (ambiguous, conflict) < 99%`.
    *   **Lý do:** Bỏ sót một cảnh báo (false negative) nguy hiểm hơn nhiều so với việc cảnh báo thừa. Hệ thống phải gần như hoàn hảo trong việc phát hiện các tình huống rủi ro để nhân viên sales có thể can thiệp.

3.  **Tỷ lệ tuân thủ schema tuyệt đối:**
    *   **Điều kiện:** `Tỷ lệ output tuân thủ schema < 100%`.
    *   **Lý do:** Output sai định dạng là lỗi cơ bản, có thể làm hỏng giao diện người dùng của Copilot.

4.  **Không có hồi quy (regression) trên các case an toàn:**
    *   **Điều kiện:** `Tỷ lệ pass trên bộ test hồi quy các lỗi P0/P1 < 100%`.
    *   **Lý do:** Bất kỳ lỗi nghiêm trọng nào đã được sửa trong quá khứ đều không được phép tái diễn.

---

Phiên bản mới sẽ bị **CẢNH BÁO (WARN)** và cần người có thẩm quyền (ví dụ: Product Manager, Sales Ops Lead) review thủ công trước khi quyết định phát hành:

1.  **Độ chính xác của việc tra cứu không giảm quá sâu:**
    *   **Điều kiện:** `Độ chính xác của việc tra cứu đúng hồ sơ < (phiên bản cũ - 5%)`.
    *   **Lý do:** Một sự sụt giảm nhẹ có thể chấp nhận được nếu phiên bản mới cải thiện ở các mặt an toàn khác, nhưng sụt giảm quá nhiều là một dấu hiệu xấu về chất lượng cốt lõi.

2.  **Chất lượng tóm tắt và gợi ý không tệ đi:**
    *   **Điều kiện:** `Điểm trung bình về chất lượng tóm tắt hoặc độ hữu ích của gợi ý (chấm bởi LLM/Human) < (phiên bản cũ - 10%)`.
    *   **Lý do:** Cần đảm bảo Copilot không chỉ an toàn mà còn phải thực sự hữu ích cho nhân viên sales.

3.  **Chi phí và độ trễ trong tầm kiểm soát:**
    *   **Điều kiện:** `Chi phí trung bình mỗi lượt phân tích > (phiên bản cũ * 1.2)` hoặc `Độ trễ P95 > (phiên bản cũ * 1.2)`.
    *   **Lý do:** Cần kiểm soát chi phí vận hành và đảm bảo trải nghiệm cho nhân viên sales không bị chậm đi đáng kể.

### 9. Kế hoạch chạy thử và dự toán chi phí

**1. Các giả định:**
*   **Model sử dụng:** Google Gemini 1.5 Flash, một model nhanh, chi phí thấp, phù hợp cho việc phân tích hội thoại, phát hiện tín hiệu và tóm tắt.
*   **Quy mô thử nghiệm:**
    *   **Bộ dữ liệu tham chiếu (Reference Dataset):** 80 hội thoại, bao gồm các ca tra cứu thành công, mơ hồ (nhiều kết quả), mâu thuẫn (dữ liệu hệ thống không khớp), và các ca rủi ro cao.
    *   **Số lần chạy lặp lại (Iterations):** 40 lần, tương ứng với các vòng lặp tinh chỉnh prompt, logic tra cứu, và quy tắc xử lý.
*   **Token trung bình mỗi hội thoại:**
    *   Input (prompt + lịch sử chat): ~800 tokens
    *   Output (JSON kết quả): ~250 tokens

**2. Dự toán chi phí:**

*   **Chi phí nhân sự (tính theo giờ công):**
    *   **PM / Thiết kế Eval (25 giờ):** Xây dựng bộ tiêu chí eval, thiết kế dataset, phân tích kết quả và đề xuất hướng đi tiếp theo. Logic tra cứu và cảnh báo phức tạp hơn case triage nên cần thêm thời gian thiết kế.
    *   **Kỹ thuật (15 giờ):** Xây dựng và duy trì eval runner, tích hợp vào CI.
    *   **Human Review (Sales Leads / Sales Ops - 30 giờ):**
        *   Tạo bộ dữ liệu vàng cho 80 cases (bao gồm tra cứu thủ công CRM/OMS để có đáp án đúng): ~10 giờ.
        *   Review các lỗi nghiêm trọng (tra cứu sai, bỏ sót cảnh báo) và các ca AI có độ tin cậy thấp qua 40 lần chạy: ~20 giờ.
    *   **Domain Expert:** 0 giờ (không áp dụng).
    *   **Tổng giờ công:** 25 + 15 + 30 = **70 giờ**.

*   **Chi phí máy (API):**
    *   **Giá API (Gemini 1.5 Flash, on-demand):**
        *   Input: $0.35 / 1 triệu tokens
        *   Output: $1.05 / 1 triệu tokens
    *   **Tổng tokens:**
        *   Input: 80 cases * 40 lần chạy * 800 tokens = 2,560,000 tokens
        *   Output: 80 cases * 40 lần chạy * 250 tokens = 800,000 tokens
    *   **Tổng chi phí API:** (2.56 * $0.35) + (0.8 * $1.05) = $0.896 + $0.84 = **$1.736**.

**3. Tổng kết:**

*   **Tổng thời gian dự kiến:** Khoảng **2 tuần**, với các vai trò làm việc song song.
*   **Tổng chi phí (chỉ tính phần cứng/API):** **~ $2**. Chi phí nhân sự (70 giờ) sẽ được tính theo lương nội bộ.

---

Tôi sử dụng giá API công khai của Google Cloud cho model Gemini 1.5 Flash tại thời điểm tháng 6/2026 để tính toán.

Với quy mô này, chi phí API gần như không đáng kể, gánh nặng chính nằm ở chi phí nhân sự (khoảng 70 giờ công). Kế hoạch này là đủ để chứng minh tính khả thi của Copilot vì nó cho phép chúng ta:
1.  **Đo lường rủi ro cốt lõi:** Với 80 cases và sự tham gia của Sales Ops, chúng ta có thể đo lường chính xác tỷ lệ tra cứu sai, tỷ lệ bỏ sót cảnh báo mơ hồ - những rủi ro vận hành lớn nhất.
2.  **Xác định mức độ hữu ích:** Đánh giá chất lượng tóm tắt và gợi ý hành động sẽ cho biết Copilot có thực sự giúp nhân viên sales tiết kiệm thời gian hay không.
3.  **Xây dựng được Release Gate an toàn:** Các kết quả từ pilot sẽ là cơ sở để định nghĩa các ngưỡng chất lượng nghiêm ngặt (ví dụ: `lỗi tra cứu sai hồ sơ = 0`) trước khi triển khai rộng hơn cho team sales.

---
