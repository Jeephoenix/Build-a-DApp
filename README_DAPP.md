# 🗳️ VoteChain — Build a Real DApp from Scratch

A complete beginner-to-intermediate guide to building a fully
functional Decentralized Voting Application (DApp) on the Ethereum
blockchain using Solidity, Hardhat, React, and Ethers.js.

---

## 📌 What Is VoteChain?

VoteChain is a blockchain-based voting application where users can:
- Create proposals for others to vote on
- Cast votes transparently on-chain
- View real-time vote counts
- Close proposals when voting ends

Every vote is permanently recorded on the blockchain — making it
tamper-proof, transparent, and trustless.

---

## 🎯 What You Will Learn

By following this guide you will learn how to:
- Write a production-ready Solidity smart contract
- Set up a professional Hardhat development environment
- Write and run unit tests for your smart contract
- Build a React frontend with MetaMask wallet connection
- Use Ethers.js to read and write data to the blockchain
- Deploy your contract to the Sepolia testnet
- Host your frontend live on Vercel or Netlify

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Smart Contract | Solidity 0.8.19 | On-chain logic & storage |
| Dev Environment | Hardhat | Compile, test & deploy |
| Frontend | React + Vite | User interface |
| Blockchain Library | Ethers.js | Talk to smart contract |
| Wallet | MetaMask | Sign transactions |
| Testnet | Sepolia | Test before mainnet |
| Frontend Hosting | Vercel / Netlify | Live deployment |
| Contract Verification | Etherscan | Public transparency |

---

## 📁 Project Structure
```
votechain/
│
├── contracts/
│   └── VoteChain.sol              ← Smart contract (Solidity)
│
├── scripts/
│   └── deploy.js                  ← Deployment script
│
├── test/
│   └── VoteChain.test.js          ← 12 unit tests
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                ← Main React component
│   │   ├── App.css                ← Full UI styles
│   │   ├── components/
│   │   │   ├── ConnectWallet.jsx  ← MetaMask connection
│   │   │   ├── CreateProposal.jsx ← Proposal form
│   │   │   ├── ProposalList.jsx   ← Display all proposals
│   │   │   └── VoteButton.jsx     ← Cast vote button
│   │   └── utils/
│   │       ├── contract.js        ← ABI & contract address
│   │       └── ethereum.js        ← MetaMask helpers
│   └── package.json
│
├── hardhat.config.js              ← Hardhat configuration
├── package.json                   ← Root dependencies
├── .env.example                   ← Environment variable template
└── README_DAPP.md                 ← This file
```

---

## ⚙️ Prerequisites

Before starting make sure you have the following installed:

- **Node.js** v18 or higher — [nodejs.org](https://nodejs.org)
- **npm** v9 or higher — comes with Node.js
- **MetaMask** browser extension — [metamask.io](https://metamask.io)
- **Git** — [git-scm.com](https://git-scm.com)
- A code editor — **VS Code** recommended ([code.visualstudio.com](https://code.visualstudio.com))

Verify your installation:
```bash
node --version     # v18+
npm --version      # 9+
git --version      # any recent version
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/crypto-safety.git
cd crypto-safety
```

### 2. Install Root Dependencies
```bash
npm install
```

### 3. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 4. Set Up Environment Variables
```bash
cp .env.example .env
```

Open `.env` and fill in your values:
```env
PRIVATE_KEY=your_metamask_private_key
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your_key
ETHERSCAN_API_KEY=your_etherscan_api_key
```

> ⚠️ **NEVER commit your `.env` file to GitHub. It is already in `.gitignore`.**

---

## 🔨 Step-by-Step Build Guide

---

### Step 1 — Compile the Smart Contract
```bash
npx hardhat compile
```

Expected output:
```
Compiled 1 Solidity file successfully ✅
```

---

### Step 2 — Run the Tests
```bash
npx hardhat test
```

Expected output:
```
  VoteChain Contract
    Deployment
      ✅ Should set the right owner
      ✅ Should start with zero proposals
    Proposals
      ✅ Should create a proposal successfully
      ✅ Should emit ProposalCreated event
      ✅ Should reject empty proposal title
      ✅ Should store correct proposal data
    Voting
      ✅ Should allow casting a vote
      ✅ Should prevent double voting
      ✅ Should track voter status correctly
      ✅ Should emit VoteCast event
      ✅ Should allow multiple voters on same proposal
    Close Proposal
      ✅ Should allow owner to close a proposal
      ✅ Should prevent voting on closed proposal
      ✅ Should prevent unauthorized closing

  14 passing ✅
```

---

### Step 3 — Start Local Blockchain

Open a **new terminal** and run:
```bash
npx hardhat node
```

This starts a local Ethereum blockchain at:
```
http://127.0.0.1:8545
```

Keep this terminal running in the background.

---

### Step 4 — Deploy Contract Locally

In your **original terminal** run:
```bash
npx hardhat run scripts/deploy.js --network hardhat
```

Expected output:
```
🚀 Starting VoteChain Deployment...

📬 Deploying with account: 0xf39Fd6e51...
💰 Account balance: 10000.0 ETH

📦 Deploying VoteChain contract...
✅ VoteChain deployed to: 0x5FbDB2315...

📄 Deployment info saved to frontend/src/utils/
🎉 Deployment Complete!
```

---

### Step 5 — Connect MetaMask to Local Network

1. Open MetaMask
2. Click the network dropdown at the top
3. Click **Add Network → Add manually**
4. Fill in:

| Field | Value |
|---|---|
| Network Name | Hardhat Local |
| RPC URL | http://127.0.0.1:8545 |
| Chain ID | 1337 |
| Currency Symbol | ETH |

5. Import a test account using one of the private keys
printed by `npx hardhat node`

---

### Step 6 — Run the Frontend
```bash
cd frontend
npm run dev
```

Open your browser at:
```
http://localhost:5173
```

You should see the VoteChain interface. Click **Connect MetaMask**
to connect your wallet and start creating proposals.

---

### Step 7 — Deploy to Sepolia Testnet

**Get free Sepolia ETH first:**
- Visit [sepoliafaucet.com](https://sepoliafaucet.com)
- Paste your MetaMask wallet address
- Receive free test ETH

**Get a free RPC URL:**
- Sign up at [alchemy.com](https://alchemy.com)
- Create a new app on Sepolia network
- Copy your RPC URL into `.env`

**Deploy:**
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

**Verify on Etherscan (optional but recommended):**
```bash
npx hardhat verify --network sepolia YOUR_CONTRACT_ADDRESS
```

---

### Step 8 — Deploy Frontend Live

**Option A — Vercel (recommended):**
```bash
cd frontend
npm run build
npm install -g vercel
vercel
```

**Option B — Netlify:**
```bash
cd frontend
npm run build
# Drag the dist/ folder to netlify.com/drop
```

Your DApp is now live for anyone in the world to use! 🌍

---

## 📄 Smart Contract Overview

### VoteChain.sol Functions

| Function | Description | Access |
|---|---|---|
| `createProposal()` | Create a new voting proposal | Anyone |
| `castVote()` | Vote on an active proposal | Anyone (once per proposal) |
| `closeProposal()` | Manually close a proposal | Owner or Creator |
| `getProposal()` | Fetch proposal details | Anyone (read-only) |
| `hasVoted()` | Check if address has voted | Anyone (read-only) |
| `getProposalCount()` | Get total proposal count | Anyone (read-only) |

### Events Emitted

| Event | Triggered When |
|---|---|
| `ProposalCreated` | A new proposal is successfully created |
| `VoteCast` | A vote is successfully cast |
| `ProposalClosed` | A proposal is manually closed |

### Security Features

- One vote per wallet address per proposal
- Only the owner or creator can close a proposal
- Proposals have a hard deadline enforced on-chain
- Empty proposal titles are rejected
- Voting on closed proposals is blocked

---

## 🐛 Common Errors & Fixes

**MetaMask not found:**
Install MetaMask from [metamask.io](https://metamask.io) and refresh.

**Insufficient funds for gas:**
Get free testnet ETH from [sepoliafaucet.com](https://sepoliafaucet.com).

**Contract not deployed to detected network:**
Make sure MetaMask is on the same network you deployed to and
`deploymentInfo.json` has the correct contract address.

**Nonce too high / Nonce mismatch:**
Go to MetaMask → Settings → Advanced → Reset Account.

**Hardhat node not running:**
Run `npx hardhat node` in a separate terminal before deploying locally.

**CORS error when calling RPC:**
Always use MetaMask as your Web3 provider — never call RPC directly.

---

## 🗺️ What to Build Next

Once VoteChain is working, here are some features you can add:

- [ ] Token-weighted voting (holders of a token get more votes)
- [ ] Delegate voting to another address
- [ ] Proposal categories and tags
- [ ] Email or push notifications for new proposals
- [ ] NFT-gated voting (only NFT holders can vote)
- [ ] Multi-chain support (Polygon, Arbitrum, Base)
- [ ] DAO treasury integration

---

## 📚 Learning Resources

| Resource | What It Covers | Link |
|---|---|---|
| CryptoZombies | Solidity basics (free, gamified) | cryptozombies.io |
| Hardhat Docs | Full Hardhat documentation | hardhat.org |
| Ethers.js Docs | Complete Ethers.js reference | docs.ethers.org |
| Ethereum Docs | Official Ethereum developer docs | ethereum.org/developers |
| Remix IDE | Browser-based Solidity editor | remix.ethereum.org |
| Alchemy University | Free Web3 developer courses | university.alchemy.com |
| OpenZeppelin | Secure contract libraries | openzeppelin.com |

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Do not use this
contract to handle real funds without a professional security audit.
Smart contract bugs can result in permanent and irreversible loss of funds.

---

## 🤝 Contributing

Contributions, suggestions, and improvements are welcome!

1. Fork the repository
2. Create a feature branch:
```bash
   git checkout -b feature/your-feature
```
3. Commit your changes:
```bash
   git commit -m "Add your feature description"
```
4. Push and open a Pull Request

---

## 📄 License

MIT License — free to use, share, and build upon.

---

## 👤 Author

Built with ❤️ for the Web3 developer community.
**Learn. Build. Deploy. Repeat.**

---

## ⭐ Support

If this guide helped you build your first DApp,
give the repo a ⭐ on GitHub — it helps others find it!
