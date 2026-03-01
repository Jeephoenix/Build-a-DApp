# dapp_build_guide.py
# A complete hands-on guide to building a real DApp from scratch
# Covers: Solidity, Hardhat, React, Ethers.js, MetaMask, Deployment

import json
import hashlib
import secrets
import time
from datetime import datetime
from typing import Optional

divider = lambda title="": print(f"\n  {'═' * 55}\n  {title}\n  {'═' * 55}" if title else f"\n  {'─' * 55}")


# ══════════════════════════════════════════════════════════
# 1. DAPP OVERVIEW & WHAT WE ARE BUILDING
# ══════════════════════════════════════════════════════════
DAPP_OVERVIEW = {
    "Project Name": "VoteChain — A Decentralized Voting DApp",
    "Description": (
        "A blockchain-based voting application where users can "
        "create proposals and vote on them transparently. "
        "Every vote is recorded on-chain and cannot be tampered with."
    ),
    "Why This Project": (
        "Voting is a perfect DApp use case because it requires "
        "transparency, immutability, and trustlessness — all core "
        "properties of a blockchain."
    ),
    "What You Will Build": [
        "A Solidity smart contract handling proposals and votes",
        "A Hardhat project for local development and testing",
        "A React frontend with wallet connection",
        "Ethers.js integration to read/write to the contract",
        "MetaMask wallet connection flow",
        "Deployment to Sepolia testnet"
    ],
    "Estimated Time": "5–10 hours for a complete beginner",
    "Difficulty": "Beginner to Intermediate"
}


# ══════════════════════════════════════════════════════════
# 2. COMPLETE PROJECT FOLDER STRUCTURE
# ══════════════════════════════════════════════════════════
PROJECT_STRUCTURE = """
  📁 votechain/
  │
  ├── 📁 contracts/
  │   └── VoteChain.sol          ← Smart contract (Solidity)
  │
  ├── 📁 scripts/
  │   └── deploy.js              ← Deployment script
  │
  ├── 📁 test/
  │   └── VoteChain.test.js      ← Contract unit tests
  │
  ├── 📁 frontend/
  │   ├── 📁 src/
  │   │   ├── App.jsx            ← Main React component
  │   │   ├── App.css            ← Styles
  │   │   ├── 📁 components/
  │   │   │   ├── ConnectWallet.jsx
  │   │   │   ├── CreateProposal.jsx
  │   │   │   ├── ProposalList.jsx
  │   │   │   └── VoteButton.jsx
  │   │   ├── 📁 utils/
  │   │   │   ├── contract.js    ← Contract ABI & address
  │   │   │   └── ethereum.js    ← MetaMask helpers
  │   │   └── main.jsx
  │   ├── index.html
  │   └── package.json
  │
  ├── hardhat.config.js          ← Hardhat configuration
  ├── package.json               ← Root dependencies
  └── .env                       ← Private keys & API keys
"""


# ══════════════════════════════════════════════════════════
# 3. COMPLETE FILE CONTENTS
# ══════════════════════════════════════════════════════════
FILE_CONTENTS = {

    # ── Smart Contract ──────────────────────────────────
    "contracts/VoteChain.sol": """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title VoteChain — Decentralized Voting Smart Contract
/// @notice Allows users to create proposals and vote on them
/// @dev Built for educational purposes

contract VoteChain {

    // ── Structs ──────────────────────────────────────
    struct Proposal {
        uint256 id;
        string title;
        string description;
        uint256 voteCount;
        address creator;
        bool active;
        uint256 createdAt;
        uint256 deadline;
    }

    struct Voter {
        bool hasVoted;
        uint256 votedProposalId;
        uint256 votedAt;
    }

    // ── State Variables ───────────────────────────────
    address public owner;
    uint256 public proposalCount;
    mapping(uint256 => Proposal) public proposals;
    mapping(address => mapping(uint256 => Voter)) public voters;
    mapping(address => uint256) public votingPower;

    // ── Events ────────────────────────────────────────
    event ProposalCreated(
        uint256 indexed id,
        string title,
        address indexed creator,
        uint256 deadline
    );

    event VoteCast(
        uint256 indexed proposalId,
        address indexed voter,
        uint256 timestamp
    );

    event ProposalClosed(
        uint256 indexed id,
        uint256 finalVoteCount
    );

    // ── Modifiers ─────────────────────────────────────
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    modifier proposalExists(uint256 _id) {
        require(_id > 0 && _id <= proposalCount, "Proposal not found");
        _;
    }

    modifier proposalActive(uint256 _id) {
        require(proposals[_id].active, "Proposal is not active");
        require(
            block.timestamp <= proposals[_id].deadline,
            "Voting deadline has passed"
        );
        _;
    }

    // ── Constructor ───────────────────────────────────
    constructor() {
        owner = msg.sender;
        votingPower[msg.sender] = 10;
    }

    // ── Functions ─────────────────────────────────────

    /// @notice Create a new voting proposal
    /// @param _title The title of the proposal
    /// @param _description Details about what is being voted on
    /// @param _durationHours How long voting stays open (in hours)
    function createProposal(
        string memory _title,
        string memory _description,
        uint256 _durationHours
    ) public {
        require(bytes(_title).length > 0, "Title cannot be empty");
        require(_durationHours >= 1, "Minimum 1 hour duration");

        proposalCount++;
        uint256 deadline = block.timestamp + (_durationHours * 1 hours);

        proposals[proposalCount] = Proposal({
            id: proposalCount,
            title: _title,
            description: _description,
            voteCount: 0,
            creator: msg.sender,
            active: true,
            createdAt: block.timestamp,
            deadline: deadline
        });

        if (votingPower[msg.sender] == 0) {
            votingPower[msg.sender] = 1;
        }

        emit ProposalCreated(
            proposalCount,
            _title,
            msg.sender,
            deadline
        );
    }

    /// @notice Cast a vote on a proposal
    /// @param _proposalId The ID of the proposal to vote on
    function castVote(uint256 _proposalId)
        public
        proposalExists(_proposalId)
        proposalActive(_proposalId)
    {
        require(
            !voters[msg.sender][_proposalId].hasVoted,
            "You have already voted on this proposal"
        );

        voters[msg.sender][_proposalId] = Voter({
            hasVoted: true,
            votedProposalId: _proposalId,
            votedAt: block.timestamp
        });

        proposals[_proposalId].voteCount++;

        emit VoteCast(_proposalId, msg.sender, block.timestamp);
    }

    /// @notice Close a proposal manually (owner or creator only)
    function closeProposal(uint256 _proposalId)
        public
        proposalExists(_proposalId)
    {
        Proposal storage proposal = proposals[_proposalId];
        require(
            msg.sender == owner || msg.sender == proposal.creator,
            "Not authorized to close this proposal"
        );
        require(proposal.active, "Already closed");

        proposal.active = false;
        emit ProposalClosed(_proposalId, proposal.voteCount);
    }

    /// @notice Get all details of a proposal
    function getProposal(uint256 _id)
        public
        view
        proposalExists(_id)
        returns (Proposal memory)
    {
        return proposals[_id];
    }

    /// @notice Check if an address has voted on a proposal
    function hasVoted(address _voter, uint256 _proposalId)
        public
        view
        returns (bool)
    {
        return voters[_voter][_proposalId].hasVoted;
    }

    /// @notice Get total number of proposals
    function getProposalCount() public view returns (uint256) {
        return proposalCount;
    }
}
""",

    # ── Hardhat Config ───────────────────────────────────
    "hardhat.config.js": """
require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    // Local Hardhat network (default)
    hardhat: {
      chainId: 1337
    },
    // Sepolia Testnet
    sepolia: {
      url: process.env.SEPOLIA_RPC_URL,
      accounts: [process.env.PRIVATE_KEY],
      chainId: 11155111
    }
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
};
""",

    # ── Deployment Script ────────────────────────────────
    "scripts/deploy.js": """
const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("\\n🚀 Starting VoteChain Deployment...\\n");

  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📬 Deploying with account:", deployer.address);

  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "ETH\\n");

  // Deploy the contract
  console.log("📦 Deploying VoteChain contract...");
  const VoteChain = await ethers.getContractFactory("VoteChain");
  const votechain = await VoteChain.deploy();
  await votechain.waitForDeployment();

  const contractAddress = await votechain.getAddress();
  console.log("✅ VoteChain deployed to:", contractAddress);

  // Save deployment info for frontend
  const deploymentInfo = {
    contractAddress,
    deployer: deployer.address,
    network: hre.network.name,
    deployedAt: new Date().toISOString(),
    abi: JSON.parse(
      fs.readFileSync(
        path.join(
          __dirname,
          "../artifacts/contracts/VoteChain.sol/VoteChain.json"
        )
      )
    ).abi
  };

  // Write to frontend utils folder
  const outputPath = path.join(
    __dirname,
    "../frontend/src/utils/deploymentInfo.json"
  );

  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
  console.log("\\n📄 Deployment info saved to frontend/src/utils/");
  console.log("\\n🎉 Deployment Complete!\\n");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });
""",

    # ── Contract Tests ───────────────────────────────────
    "test/VoteChain.test.js": """
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("VoteChain Contract", function () {
  let votechain;
  let owner, voter1, voter2;

  // Deploy fresh contract before each test
  beforeEach(async function () {
    [owner, voter1, voter2] = await ethers.getSigners();
    const VoteChain = await ethers.getContractFactory("VoteChain");
    votechain = await VoteChain.deploy();
    await votechain.waitForDeployment();
  });

  // ── Deployment Tests ──────────────────────────────
  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await votechain.owner()).to.equal(owner.address);
    });

    it("Should start with zero proposals", async function () {
      expect(await votechain.getProposalCount()).to.equal(0);
    });
  });

  // ── Proposal Tests ────────────────────────────────
  describe("Proposals", function () {
    it("Should create a proposal successfully", async function () {
      await votechain.createProposal(
        "Add Dark Mode",
        "Should the app support dark mode?",
        24
      );
      expect(await votechain.getProposalCount()).to.equal(1);
    });

    it("Should emit ProposalCreated event", async function () {
      await expect(
        votechain.createProposal("Test Proposal", "Description", 24)
      ).to.emit(votechain, "ProposalCreated");
    });

    it("Should reject empty proposal title", async function () {
      await expect(
        votechain.createProposal("", "Description", 24)
      ).to.be.revertedWith("Title cannot be empty");
    });

    it("Should store correct proposal data", async function () {
      await votechain.createProposal("My Proposal", "Details here", 48);
      const proposal = await votechain.getProposal(1);
      expect(proposal.title).to.equal("My Proposal");
      expect(proposal.voteCount).to.equal(0);
      expect(proposal.active).to.be.true;
    });
  });

  // ── Voting Tests ──────────────────────────────────
  describe("Voting", function () {
    beforeEach(async function () {
      await votechain.createProposal("Test Vote", "Vote on this", 24);
    });

    it("Should allow casting a vote", async function () {
      await votechain.connect(voter1).castVote(1);
      const proposal = await votechain.getProposal(1);
      expect(proposal.voteCount).to.equal(1);
    });

    it("Should prevent double voting", async function () {
      await votechain.connect(voter1).castVote(1);
      await expect(
        votechain.connect(voter1).castVote(1)
      ).to.be.revertedWith("You have already voted on this proposal");
    });

    it("Should track voter status correctly", async function () {
      expect(await votechain.hasVoted(voter1.address, 1)).to.be.false;
      await votechain.connect(voter1).castVote(1);
      expect(await votechain.hasVoted(voter1.address, 1)).to.be.true;
    });

    it("Should emit VoteCast event", async function () {
      await expect(
        votechain.connect(voter1).castVote(1)
      ).to.emit(votechain, "VoteCast");
    });

    it("Should allow multiple voters on same proposal", async function () {
      await votechain.connect(voter1).castVote(1);
      await votechain.connect(voter2).castVote(1);
      const proposal = await votechain.getProposal(1);
      expect(proposal.voteCount).to.equal(2);
    });
  });

  // ── Close Proposal Tests ──────────────────────────
  describe("Close Proposal", function () {
    beforeEach(async function () {
      await votechain.createProposal("Close Test", "Test closing", 24);
    });

    it("Should allow owner to close a proposal", async function () {
      await votechain.closeProposal(1);
      const proposal = await votechain.getProposal(1);
      expect(proposal.active).to.be.false;
    });

    it("Should prevent voting on closed proposal", async function () {
      await votechain.closeProposal(1);
      await expect(
        votechain.connect(voter1).castVote(1)
      ).to.be.revertedWith("Proposal is not active");
    });

    it("Should prevent unauthorized closing", async function () {
      await expect(
        votechain.connect(voter1).closeProposal(1)
      ).to.be.revertedWith("Not authorized to close this proposal");
    });
  });
});
""",

    # ── React App.jsx ─────────────────────────────────────
    "frontend/src/App.jsx": """
import { useState, useEffect } from "react";
import { ethers } from "ethers";
import ConnectWallet from "./components/ConnectWallet";
import CreateProposal from "./components/CreateProposal";
import ProposalList from "./components/ProposalList";
import deploymentInfo from "./utils/deploymentInfo.json";
import "./App.css";

function App() {
  const [provider, setProvider]     = useState(null);
  const [signer, setSigner]         = useState(null);
  const [contract, setContract]     = useState(null);
  const [account, setAccount]       = useState(null);
  const [proposals, setProposals]   = useState([]);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");

  // Connect MetaMask wallet
  const connectWallet = async () => {
    try {
      if (!window.ethereum) {
        setError("MetaMask not found. Please install it.");
        return;
      }

      setLoading(true);
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts"
      });

      const _provider = new ethers.BrowserProvider(window.ethereum);
      const _signer   = await _provider.getSigner();
      const _contract = new ethers.Contract(
        deploymentInfo.contractAddress,
        deploymentInfo.abi,
        _signer
      );

      setProvider(_provider);
      setSigner(_signer);
      setContract(_contract);
      setAccount(accounts[0]);
      setError("");

      await loadProposals(_contract);
    } catch (err) {
      setError("Failed to connect wallet: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Load all proposals from contract
  const loadProposals = async (_contract) => {
    try {
      setLoading(true);
      const count = await _contract.getProposalCount();
      const loaded = [];

      for (let i = 1; i <= Number(count); i++) {
        const proposal = await _contract.getProposal(i);
        loaded.push({
          id: Number(proposal.id),
          title: proposal.title,
          description: proposal.description,
          voteCount: Number(proposal.voteCount),
          creator: proposal.creator,
          active: proposal.active,
          deadline: new Date(
            Number(proposal.deadline) * 1000
          ).toLocaleString()
        });
      }

      setProposals(loaded);
    } catch (err) {
      setError("Failed to load proposals: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Create a new proposal
  const createProposal = async (title, description, hours) => {
    try {
      setLoading(true);
      const tx = await contract.createProposal(title, description, hours);
      await tx.wait();
      await loadProposals(contract);
    } catch (err) {
      setError("Failed to create proposal: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Cast a vote
  const castVote = async (proposalId) => {
    try {
      setLoading(true);
      const tx = await contract.castVote(proposalId);
      await tx.wait();
      await loadProposals(contract);
    } catch (err) {
      setError("Failed to cast vote: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  // Listen for account changes in MetaMask
  useEffect(() => {
    if (window.ethereum) {
      window.ethereum.on("accountsChanged", (accounts) => {
        setAccount(accounts[0] || null);
        if (!accounts[0]) {
          setSigner(null);
          setContract(null);
        }
      });
    }
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>🗳️ VoteChain</h1>
        <p>Decentralized Voting on the Blockchain</p>
        <ConnectWallet
          account={account}
          onConnect={connectWallet}
          loading={loading}
        />
      </header>

      {error && (
        <div className="error-banner">
          ⚠️ {error}
          <button onClick={() => setError("")}>✕</button>
        </div>
      )}

      {account && (
        <main className="app-main">
          <CreateProposal onCreate={createProposal} loading={loading} />
          <ProposalList
            proposals={proposals}
            onVote={castVote}
            account={account}
            loading={loading}
          />
        </main>
      )}

      {!account && (
        <div className="connect-prompt">
          <h2>👋 Welcome to VoteChain</h2>
          <p>Connect your MetaMask wallet to start voting.</p>
        </div>
      )}
    </div>
  );
}

export default App;
""",

    # ── ConnectWallet Component ───────────────────────────
    "frontend/src/components/ConnectWallet.jsx": """
function ConnectWallet({ account, onConnect, loading }) {
  const shortAddress = (addr) =>
    addr ? addr.slice(0, 6) + "..." + addr.slice(-4) : "";

  return (
    <div className="wallet-container">
      {account ? (
        <div className="wallet-connected">
          <span className="dot green"></span>
          <span>Connected: {shortAddress(account)}</span>
        </div>
      ) : (
        <button
          className="btn btn-primary"
          onClick={onConnect}
          disabled={loading}
        >
          {loading ? "Connecting..." : "🦊 Connect MetaMask"}
        </button>
      )}
    </div>
  );
}

export default ConnectWallet;
""",

    # ── CreateProposal Component ──────────────────────────
    "frontend/src/components/CreateProposal.jsx": """
import { useState } from "react";

function CreateProposal({ onCreate, loading }) {
  const [title, setTitle]         = useState("");
  const [description, setDesc]    = useState("");
  const [hours, setHours]         = useState(24);
  const [isOpen, setIsOpen]       = useState(false);

  const handleSubmit = async () => {
    if (!title.trim()) return alert("Please enter a proposal title.");
    await onCreate(title, description, hours);
    setTitle("");
    setDesc("");
    setHours(24);
    setIsOpen(false);
  };

  return (
    <div className="create-proposal">
      <button
        className="btn btn-secondary"
        onClick={() => setIsOpen(!isOpen)}
      >
        {isOpen ? "✕ Cancel" : "+ New Proposal"}
      </button>

      {isOpen && (
        <div className="proposal-form">
          <h3>📝 Create New Proposal</h3>

          <input
            type="text"
            placeholder="Proposal title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={100}
          />

          <textarea
            placeholder="Describe what you are voting on..."
            value={description}
            onChange={(e) => setDesc(e.target.value)}
            rows={4}
          />

          <label>
            Voting Duration: {hours} hours
            <input
              type="range"
              min={1}
              max={168}
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
            />
          </label>

          <button
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={loading || !title.trim()}
          >
            {loading ? "Creating..." : "🚀 Create Proposal"}
          </button>
        </div>
      )}
    </div>
  );
}

export default CreateProposal;
""",

    # ── ProposalList Component ────────────────────────────
    "frontend/src/components/ProposalList.jsx": """
function ProposalList({ proposals, onVote, account, loading }) {
  if (proposals.length === 0) {
    return (
      <div className="empty-state">
        <p>🗳️ No proposals yet. Create the first one!</p>
      </div>
    );
  }

  return (
    <div className="proposal-list">
      <h2>📋 Active Proposals ({proposals.length})</h2>
      {proposals.map((proposal) => (
        <div
          key={proposal.id}
          className={`proposal-card ${!proposal.active ? "inactive" : ""}`}
        >
          <div className="proposal-header">
            <span className="proposal-id">#{proposal.id}</span>
            <span className={`badge ${proposal.active ? "active" : "closed"}`}>
              {proposal.active ? "🟢 Active" : "🔴 Closed"}
            </span>
          </div>

          <h3>{proposal.title}</h3>
          <p>{proposal.description}</p>

          <div className="proposal-meta">
            <span>👤 {proposal.creator.slice(0, 10)}...</span>
            <span>⏰ Deadline: {proposal.deadline}</span>
          </div>

          <div className="proposal-footer">
            <div className="vote-count">
              🗳️ <strong>{proposal.voteCount}</strong> votes
            </div>
            {proposal.active && (
              <button
                className="btn btn-vote"
                onClick={() => onVote(proposal.id)}
                disabled={loading}
              >
                {loading ? "Voting..." : "✅ Vote"}
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

export default ProposalList;
""",

    # ── App CSS ───────────────────────────────────────────
    "frontend/src/App.css": """
* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', sans-serif;
  background: #0f0f1a;
  color: #e2e8f0;
  min-height: 100vh;
}

.app { max-width: 900px; margin: 0 auto; padding: 20px; }

.app-header {
  text-align: center;
  padding: 40px 20px;
  border-bottom: 1px solid #2d3748;
  margin-bottom: 30px;
}

.app-header h1 { font-size: 2.5rem; color: #7c3aed; margin-bottom: 8px; }
.app-header p  { color: #94a3b8; margin-bottom: 20px; }

.btn {
  padding: 10px 20px; border: none; border-radius: 8px;
  cursor: pointer; font-size: 14px; font-weight: 600;
  transition: all 0.2s;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-primary  { background: #7c3aed; color: white; }
.btn-primary:hover:not(:disabled)  { background: #6d28d9; }
.btn-secondary { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; }
.btn-secondary:hover { background: #334155; }
.btn-vote  { background: #059669; color: white; }
.btn-vote:hover:not(:disabled)  { background: #047857; }

.wallet-connected {
  display: flex; align-items: center; gap: 8px;
  background: #1e293b; padding: 8px 16px; border-radius: 20px;
  display: inline-flex;
}

.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot.green { background: #10b981; }

.error-banner {
  background: #7f1d1d; color: #fca5a5; padding: 12px 16px;
  border-radius: 8px; margin-bottom: 20px;
  display: flex; justify-content: space-between; align-items: center;
}

.app-main { display: flex; flex-direction: column; gap: 24px; }

.connect-prompt {
  text-align: center; padding: 80px 20px;
}

.connect-prompt h2 { font-size: 1.8rem; margin-bottom: 12px; }
.connect-prompt p  { color: #94a3b8; }

.proposal-form {
  background: #1e293b; border-radius: 12px; padding: 24px;
  margin-top: 16px; display: flex; flex-direction: column; gap: 16px;
}

.proposal-form input,
.proposal-form textarea {
  background: #0f172a; border: 1px solid #334155; border-radius: 8px;
  padding: 12px; color: #e2e8f0; font-size: 14px; width: 100%;
}

.proposal-form input:focus,
.proposal-form textarea:focus {
  outline: none; border-color: #7c3aed;
}

.proposal-list h2 { margin-bottom: 16px; font-size: 1.2rem; }

.proposal-card {
  background: #1e293b; border-radius: 12px; padding: 20px;
  margin-bottom: 16px; border: 1px solid #334155;
  transition: border-color 0.2s;
}

.proposal-card:hover { border-color: #7c3aed; }
.proposal-card.inactive { opacity: 0.6; }

.proposal-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 12px;
}

.proposal-id { color: #64748b; font-size: 12px; }

.badge {
  padding: 4px 10px; border-radius: 20px;
  font-size: 12px; font-weight: 600;
}

.badge.active { background: #064e3b; color: #6ee7b7; }
.badge.closed { background: #7f1d1d; color: #fca5a5; }

.proposal-card h3 { font-size: 1.1rem; margin-bottom: 8px; }
.proposal-card p  { color: #94a3b8; font-size: 14px; margin-bottom: 12px; }

.proposal-meta {
  display: flex; gap: 16px; font-size: 12px;
  color: #64748b; margin-bottom: 16px;
}

.proposal-footer {
  display: flex; justify-content: space-between; align-items: center;
}

.vote-count { color: #94a3b8; font-size: 14px; }

.empty-state {
  text-align: center; padding: 60px; color: #64748b;
  background: #1e293b; border-radius: 12px;
}
""",

    # ── package.json ──────────────────────────────────────
    "package.json": """
{
  "name": "votechain",
  "version": "1.0.0",
  "description": "Decentralized Voting DApp",
  "scripts": {
    "compile": "hardhat compile",
    "test": "hardhat test",
    "node": "hardhat node",
    "deploy:local": "hardhat run scripts/deploy.js --network hardhat",
    "deploy:sepolia": "hardhat run scripts/deploy.js --network sepolia"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^4.0.0",
    "hardhat": "^2.19.0",
    "chai": "^4.3.7",
    "dotenv": "^16.3.1"
  }
}
""",

    # ── .env Template ─────────────────────────────────────
    ".env.example": """
# !! NEVER commit your real .env to GitHub !!
# Copy this file to .env and fill in your values

# Your wallet private key (from MetaMask — Export Account)
PRIVATE_KEY=your_private_key_here

# Sepolia RPC URL (get from Alchemy or Infura — free tier)
SEPOLIA_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/your_api_key

# Etherscan API Key (for contract verification — free)
ETHERSCAN_API_KEY=your_etherscan_api_key
"""
}


# ══════════════════════════════════════════════════════════
# 4. STEP BY STEP BUILD GUIDE
# ══════════════════════════════════════════════════════════
BUILD_STEPS = [
    {
        "step": "Step 1 — Install Prerequisites",
        "commands": [
            "# Install Node.js from nodejs.org (v18 or higher)",
            "node --version          # Should show v18+",
            "npm --version           # Should show 9+",
            "# Install MetaMask from metamask.io"
        ],
        "notes": "Make sure Node.js is installed before anything else."
    },
    {
        "step": "Step 2 — Create Project & Install Hardhat",
        "commands": [
            "mkdir votechain && cd votechain",
            "npm init -y",
            "npm install --save-dev hardhat",
            "npx hardhat init",
            "# Choose: Create a JavaScript project",
            "# Press Enter to accept defaults"
        ],
        "notes": "Hardhat is your local Ethereum development environment."
    },
    {
        "step": "Step 3 — Install Dependencies",
        "commands": [
            "npm install --save-dev @nomicfoundation/hardhat-toolbox",
            "npm install dotenv",
            "# For frontend:",
            "cd frontend",
            "npm create vite@latest . -- --template react",
            "npm install",
            "npm install ethers"
        ],
        "notes": "Ethers.js lets your React app talk to the blockchain."
    },
    {
        "step": "Step 4 — Write the Smart Contract",
        "commands": [
            "# Create contracts/VoteChain.sol",
            "# Paste the Solidity code from this guide",
            "npx hardhat compile",
            "# Should output: Compiled 1 Solidity file successfully"
        ],
        "notes": "Fix any compilation errors before moving forward."
    },
    {
        "step": "Step 5 — Run Tests",
        "commands": [
            "# Create test/VoteChain.test.js",
            "# Paste the test code from this guide",
            "npx hardhat test",
            "# All 12 tests should pass ✅"
        ],
        "notes": "Never skip tests. They protect you from costly bugs."
    },
    {
        "step": "Step 6 — Deploy Locally",
        "commands": [
            "# Terminal 1 — Start local blockchain",
            "npx hardhat node",
            "# Terminal 2 — Deploy contract",
            "npx hardhat run scripts/deploy.js --network hardhat",
            "# Copy the contract address from the output"
        ],
        "notes": "Local deployment is free and instant. Test everything here first."
    },
    {
        "step": "Step 7 — Build the Frontend",
        "commands": [
            "# Create all React components from this guide",
            "# Update frontend/src/utils/deploymentInfo.json",
            "cd frontend && npm run dev",
            "# Open http://localhost:5173 in your browser"
        ],
        "notes": "Make sure MetaMask is set to Localhost 8545 network."
    },
    {
        "step": "Step 8 — Deploy to Sepolia Testnet",
        "commands": [
            "# 1. Get Sepolia ETH: sepoliafaucet.com",
            "# 2. Get free RPC URL: alchemy.com",
            "# 3. Create .env file with your keys",
            "npx hardhat run scripts/deploy.js --network sepolia",
            "# 4. Verify on Etherscan:",
            "npx hardhat verify --network sepolia CONTRACT_ADDRESS"
        ],
        "notes": "Never use mainnet until fully tested on testnet."
    },
    {
        "step": "Step 9 — Deploy Frontend",
        "commands": [
            "cd frontend",
            "npm run build",
            "# Option A — Vercel (recommended):",
            "npm install -g vercel && vercel",
            "# Option B — Netlify:",
            "# Drag the dist/ folder to netlify.com/drop"
        ],
        "notes": "Your DApp is now live for anyone to use!"
    }
]


# ══════════════════════════════════════════════════════════
# 5. COMMON ERRORS & FIXES
# ══════════════════════════════════════════════════════════
COMMON_ERRORS = [
    {
        "error": "MetaMask not found / window.ethereum is undefined",
        "cause": "MetaMask extension not installed in browser.",
        "fix": "Install MetaMask from metamask.io and refresh the page."
    },
    {
        "error": "Transaction reverted: insufficient funds",
        "cause": "Wallet doesn't have enough ETH to pay gas fees.",
        "fix": "Get testnet ETH from sepoliafaucet.com or add ETH to your wallet."
    },
    {
        "error": "Contract not deployed to detected network",
        "cause": "Frontend is pointing to wrong network or contract address.",
        "fix": "Check deploymentInfo.json has the correct address and your MetaMask is on the right network."
    },
    {
        "error": "Nonce too high / Nonce mismatch",
        "cause": "MetaMask nonce is out of sync with local Hardhat node.",
        "fix": "Go to MetaMask → Settings → Advanced → Reset Account."
    },
    {
        "error": "HardhatError: Cannot connect to the network",
        "cause": "Local Hardhat node is not running.",
        "fix": "Run npx hardhat node in a separate terminal first."
    },
    {
        "error": "Error: invalid address",
        "cause": "Contract address in code is wrong or missing.",
        "fix": "Copy the exact contract address printed after deployment."
    },
    {
        "error": "CORS error when calling RPC",
        "cause": "Calling blockchain RPC directly from browser without provider.",
        "fix": "Always use MetaMask or a Web3 provider — never raw fetch calls."
    }
]


# ══════════════════════════════════════════════════════════
# 6. DISPLAY FUNCTIONS
# ══════════════════════════════════════════════════════════
def display_overview() -> None:
    divider("📌 DAPP PROJECT OVERVIEW")
    print(f"\n  🏗️  Project   : {DAPP_OVERVIEW['Project Name']}")
    print(f"  📝 What      : {DAPP_OVERVIEW['Description']}")
    print(f"  ⏱️  Time      : {DAPP_OVERVIEW['Estimated Time']}")
    print(f"  📊 Difficulty: {DAPP_OVERVIEW['Difficulty']}")
    print(f"\n  🎯 You will build:")
    for item in DAPP_OVERVIEW["What You Will Build"]:
        print(f"    ✅ {item}")


def display_project_structure() -> None:
    divider("📁 PROJECT FOLDER STRUCTURE")
    print(PROJECT_STRUCTURE)


def display_build_steps() -> None:
    divider("🛠️  STEP BY STEP BUILD GUIDE")
    for phase in BUILD_STEPS:
        print(f"\n  🔷 {phase['step']}")
        print(f"  💡 {phase['notes']}")
        print(f"  {'─' * 50}")
        for cmd in phase["commands"]:
            print(f"    $ {cmd}" if not cmd.startswith("#") else f"    {cmd}")


def display_file_preview(filename: str) -> None:
    if filename in FILE_CONTENTS:
        divider(f"📄 FILE: {filename}")
        lines = FILE_CONTENTS[filename].strip().split("\n")
        for line in lines[:40]:
            print(f"  {line}")
        if len(lines) > 40:
            print(f"\n  ... ({len(lines) - 40} more lines)")
    else:
        print(f"  ❌ File {filename} not found.")


def display_common_errors() -> None:
    divider("🐛 COMMON ERRORS & HOW TO FIX THEM")
    for i, item in enumerate(COMMON_ERRORS, 1):
        print(f"\n  ❌ Error {i}  : {item['error']}")
        print(f"  🔍 Cause   : {item['cause']}")
        print(f"  ✅ Fix     : {item['fix']}")


def display_all_files() -> None:
    divider("📦 ALL PROJECT FILES")
    print(f"\n  This guide contains {len(FILE_CONTENTS)} complete files:\n")
    for i, filename in enumerate(FILE_CONTENTS.keys(), 1):
        lines = len(FILE_CONTENTS[filename].strip().split("\n"))
        print(f"  {i:>2}. 📄 {filename:<45} ({lines} lines)")


# ══════════════════════════════════════════════════════════
# 7. MAIN RUNNER
# ══════════════════════════════════════════════════════════
def main():
    print("\n" + "=" * 60)
    print("   🌐 How to Build a Real DApp — VoteChain Complete Guide")
    print("=" * 60)

    # Overview
    display_overview()

    # Project structure
    display_project_structure()

    # All files list
    display_all_files()

    # Preview key files
    print("\n\n  📌 SMART CONTRACT PREVIEW")
    display_file_preview("contracts/VoteChain.sol")

    print("\n\n  📌 REACT APP PREVIEW")
    display_file_preview("frontend/src/App.jsx")

    # Build steps
    display_build_steps()

    # Common errors
    display_common_errors()

    print("\n\n" + "=" * 60)
    print("  🎓 VoteChain DApp Build Guide Complete!")
    print("  🚀 Follow the 9 steps above to build your real DApp.")
    print("  💡 Tip: Start local, test thoroughly, then go to testnet.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
```

---

**Step-by-Step Commit Guide on Mobile:**

**Step 1 —** Go to your `crypto-safety` repo on [github.com](https://github.com).

**Step 2 —** Tap **Add file → Create new file**.

**Step 3 —** Name the file `dapp_build_guide.py`

**Step 4 —** Paste the full code into the content area.

**Step 5 —** Write your commit message:
```
Add complete VoteChain DApp build guide with Solidity contract, Hardhat setup, React frontend, Ethers.js integration, tests, deployment scripts, and error troubleshooting
