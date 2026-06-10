import random
import streamlit as st

# --- 定数定義 ---
BET_AMOUNT = 10000

CARD_VALUES = {
    "A": 11,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
}


# --- 関数定義: ストラテジー判定 ---
def get_correct_action(player_cards, dealer_up_card):
    """ベーシックストラテジーに基づく正解アクションを返す (H:ヒット, S:スタンド, D:ダブル, P:スプリット)"""
    d_val = CARD_VALUES[dealer_up_card]

    # 1. ペアハンドの判定
    if len(player_cards) == 2 and player_cards[0] == player_cards[1]:
        p_card = player_cards[0]
        if p_card in ["A", "8"]:
            return "P"
        elif p_card in ["10", "J", "Q", "K"]:
            return "S"
        elif p_card == "9":
            return "S" if d_val in [7, 10, 11] else "P"
        elif p_card == "7":
            return "P" if d_val <= 7 else "H"
        elif p_card == "6":
            return "P" if d_val <= 6 else "H"
        elif p_card == "5":
            return "D" if d_val <= 9 else "H"
        elif p_card == "4":
            return "P" if d_val in [5, 6] else "H"
        elif p_card in ["2", "3"]:
            return "P" if d_val <= 7 else "H"

    # カードの合計とAの有無をチェック
    values = [CARD_VALUES[c] for c in player_cards]
    total = sum(values)
    ace_count = player_cards.count("A")

    # Aを1に変換する処理（バースト防止）
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 10

    # 2. ソフトハンドの判定 (Aを11として数えている場合)
    if ace_count > 0 and total <= 21:
        # totalは「Aを11とした合計」
        other_total = total - 11
        if other_total >= 8:
            return "S"
        elif other_total == 7:
            return "D" if d_val <= 6 else "S" if d_val in [7, 8] else "H"
        elif other_total == 6:
            return "D" if d_val <= 6 else "H"
        elif other_total in [4, 5]:
            return "D" if d_val in [4, 5, 6] else "H"
        elif other_total in [2, 3]:
            return "D" if d_val in [5, 6] else "H"

    # 3. ハードハンドの判定
    if total >= 17:
        return "S"
    elif total == 16:
        return "S" if d_val <= 6 else "H"
    elif total == 15:
        return "S" if d_val <= 6 else "H"
    elif total == 14:
        return "S" if d_val <= 6 else "H"
    elif total == 13:
        return "S" if d_val <= 6 else "H"
    elif total == 12:
        return "S" if d_val in [4, 5, 6] else "H"
    elif total == 11:
        return "D"
    elif total == 10:
        return "D" if d_val <= 9 else "H"
    elif total == 9:
        return "D" if d_val <= 6 else "H"
    else:
        return "H"


def draw_card():
    """常に1/13の確率でカードをランダムに引く"""
    return random.choice(list(CARD_VALUES.keys()))


def calculate_total(cards):
    """手札の合計値を計算（Aの調整あり）"""
    total = sum(CARD_VALUES[c] for c in cards)
    ace_count = cards.count("A")
    while total > 21 and ace_count > 0:
        total -= 10
        ace_count -= 1
    return total


# --- Streamlit 画面構築 ---
st.title("stg")

# セッション状態の初期化
if "total_profit" not in st.session_state:
    st.session_state.total_profit = 0
if "wins" not in st.session_state:
    st.session_state.wins = 0
if "losses" not in st.session_state:
    st.session_state.losses = 0
if "draws" not in st.session_state:
    st.session_state.draws = 0
if "total_actions" not in st.session_state:
    st.session_state.total_actions = 0
if "correct_actions" not in st.session_state:
    st.session_state.correct_actions = 0
if "game_status" not in st.session_state:
    st.session_state.game_status = "init"  # init, player_turn, dealer_turn, end

# 新しいゲームの開始
if st.session_state.game_status == "init":
    st.session_state.dealer_hand = [draw_card(), draw_card()]
    st.session_state.player_hands = [[draw_card(), draw_card()]]  # 手札のリスト
    st.session_state.hand_bets = [BET_AMOUNT]  # 各手札の賭け金
    st.session_state.current_hand_idx = 0
    st.session_state.history = []
    st.session_state.game_status = "player_turn"

# サイドバー：スコアボード表示
st.sidebar.metric("通算収支", f"{st.session_state.total_profit:,} 円")

# 勝敗内訳の表示
st.sidebar.metric(
    "勝敗内訳",
    f"{st.session_state.wins}勝 {st.session_state.losses}敗 {st.session_state.draws}分",
)

# 正解率の計算と表示
if st.session_state.total_actions > 0:
    accuracy = (
        st.session_state.correct_actions / st.session_state.total_actions
    ) * 100
    st.sidebar.metric(
        "ストラテジー正解率",
        f"{accuracy:.1f} %",
        help=f"{st.session_state.correct_actions} / {st.session_state.total_actions}",
    )
else:
    st.sidebar.metric("ストラテジー正解率", "0.0 %")

if st.sidebar.button("データをリセット"):
    st.session_state.total_profit = 0
    st.session_state.wins = 0
    st.session_state.losses = 0
    st.session_state.draws = 0
    st.session_state.total_actions = 0
    st.session_state.correct_actions = 0
    st.rerun()

# 盤面の表示
dealer_up = st.session_state.dealer_hand[0]
st.subheader("【Dアップカード】")
st.markdown(f"### ` [ {dealer_up} ] `")

st.write("---")
st.subheader("【hand】")

for idx, hand in enumerate(st.session_state.player_hands):
    total = calculate_total(hand)
    hand_str = " ".join([f"`[ {c} ]`" for c in hand])

    # 現在操作中の手に矢印をつける
    if (
        st.session_state.game_status == "player_turn"
        and idx == st.session_state.current_hand_idx
    ):
        st.markdown(f"👉 **手札 {idx+1}:** {hand_str} (合計: **{total}**) ※操作中")
    else:
        st.markdown(f"  **手札 {idx+1}:** {hand_str} (合計: **{total}**)")

st.write("---")

# ログ・判定メッセージの表示エリア
for msg, msg_type in st.session_state.history:
    if msg_type == "success":
        st.success(msg)
    elif msg_type == "error":
        st.error(msg)
    else:
        st.info(msg)

# --- プレイヤーのターン ---
if st.session_state.game_status == "player_turn":
    idx = st.session_state.current_hand_idx
    current_hand = st.session_state.player_hands[idx]

    # 正解の判定
    correct_action = get_correct_action(current_hand, dealer_up)

    # アクション選択ボタン
    col1, col2, col3, col4 = st.columns(4)

    # 利用可能なボタンの制御（スプリットとダブルは最初の2枚の時だけ）
    allow_split = len(current_hand) == 2 and current_hand[0] == current_hand[1]
    allow_double = len(current_hand) == 2 and len(st.session_state.player_hands) == 1

    action = None
    with col1:
        if st.button("H: ヒット", use_container_width=True):
            action = "H"
    with col2:
        if st.button("S: スタンド", use_container_width=True):
            action = "S"
    with col3:
        if st.button(
            "D: ダブル", disabled=not allow_double, use_container_width=True
        ):
            action = "D"
    with col4:
        if st.button(
            "P: スプリット", disabled=not allow_split, use_container_width=True
        ):
            action = "P"

    if action:
        # アクションの集計
        st.session_state.total_actions += 1

        # ストラテジー答え合わせ
        action_names = {
            "H": "ヒット",
            "S": "スタンド",
            "D": "ダブルダウン",
            "P": "スプリット",
        }
        if action == correct_action:
            st.session_state.correct_actions += 1
            st.session_state.history.append(
                (
                    f"【判定】正解です！ セオリー通りの「{action_names[correct_action]}」です。",
                    "success",
                )
            )
        else:
            st.session_state.history.append(
                (
                    f"【判定】ミス！ あなたの選択: {action_names[action]} ➡ 正解は「{action_names[correct_action]}」でした。",
                    "error",
                )
            )

        # アクションごとの処理
        if action == "H":
            current_hand.append(draw_card())
            if calculate_total(current_hand) > 21:
                st.session_state.history.append(
                    (f"手札 {idx+1} がバーストしました！", "error")
                )
                # 次の手札へ、なければディーラーのターンへ
                if idx + 1 < len(st.session_state.player_hands):
                    st.session_state.current_hand_idx += 1
                else:
                    st.session_state.game_status = "dealer_turn"
            st.rerun()

        elif action == "S":
            if idx + 1 < len(st.session_state.player_hands):
                st.session_state.current_hand_idx += 1
            else:
                st.session_state.game_status = "dealer_turn"
            st.rerun()

        elif action == "D":
            st.session_state.hand_bets[idx] *= 2
            current_hand.append(draw_card())
            st.session_state.game_status = "dealer_turn"
            st.rerun()

        elif action == "P":
            # スプリット処理（本格版）
            card1, card2 = current_hand[0], current_hand[1]
            # 新しい2つの手を生成（それぞれ1枚追加）
            st.session_state.player_hands = [
                [card1, draw_card()],
                [card2, draw_card()],
            ]
            st.session_state.hand_bets = [BET_AMOUNT, BET_AMOUNT]
            st.rerun()

# --- ディーラーのターン ＆ 結果判定 ---
if st.session_state.game_status == "dealer_turn":
    # ディーラーがカードを引く（全プレイヤーの手がバーストしてない場合のみ17まで引く）
    all_busted = all(
        calculate_total(h) > 21 for h in st.session_state.player_hands
    )

    if not all_busted:
        while calculate_total(st.session_state.dealer_hand) < 17:
            st.session_state.dealer_hand.append(draw_card())

    d_total = calculate_total(st.session_state.dealer_hand)
    d_hand_str = " ".join([f"`[ {c} ]`" for c in st.session_state.dealer_hand])

    st.write("---")
    st.subheader("【ディーラーの最終手札】")
    st.markdown(f"{d_hand_str} (合計: **{d_total}**)")

    # 各手札の勝敗判定
    round_profit = 0
    for idx, hand in enumerate(st.session_state.player_hands):
        p_total = calculate_total(hand)
        bet = st.session_state.hand_bets[idx]

        if p_total > 21:
            # プレイヤーバースト（既に確定）
            round_profit -= bet
            st.session_state.losses += 1
            st.session_state.history.append(
                (f"手札 {idx+1}: バースト負け (-{bet:,}円)", "normal")
            )
        elif d_total > 21:
            # ディーラーバースト
            round_profit += bet
            st.session_state.wins += 1
            st.session_state.history.append(
                (f"手札 {idx+1}: ディーラーバーストで勝利 (+{bet:,}円)", "success")
            )
        elif p_total > d_total:
            # 勝ち
            round_profit += bet
            st.session_state.wins += 1
            st.session_state.history.append(
                (f"手札 {idx+1}: 勝利！ (+{bet:,}円)", "success")
            )
        elif p_total < d_total:
            # 負け
            round_profit -= bet
            st.session_state.losses += 1
            st.session_state.history.append(
                (f"手札 {idx+1}: 負け (-{bet:,}円)", "normal")
            )
        else:
            # 引き分け
            st.session_state.draws += 1
            st.session_state.history.append(
                (f"手札 {idx+1}: 引き分け (プッシュ)", "normal")
            )

    st.session_state.total_profit += round_profit
    st.session_state.game_status = "end"
    st.rerun()

# --- ゲーム終了（次のゲームへ） ---
if st.session_state.game_status == "end":
    # ディーラーの手札を再表示
    d_total = calculate_total(st.session_state.dealer_hand)
    d_hand_str = " ".join([f"`[ {c} ]`" for c in st.session_state.dealer_hand])
    st.write("---")
    st.subheader("【ディーラーの最終手札】")
    st.markdown(f"{d_hand_str} (合計: **{d_total}**)")

    if st.button("次のゲームへ", type="primary", use_container_width=True):
        st.session_state.game_status = "init"
        st.rerun()
