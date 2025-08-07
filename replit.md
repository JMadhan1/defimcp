# Overview

This project is a DeFi MCP (Model Context Protocol) Server that enables AI agents to perform cross-chain decentralized finance operations. The system provides a unified interface for trading, lending, and yield farming across multiple blockchains including Ethereum, Polygon, and Solana. Built as both a web application and MCP server, it offers REST APIs and MCP protocol endpoints for automated DeFi interactions.

**Status:** ✅ Application running successfully on port 5000  
**Last Updated:** August 5, 2025  
**Ready for:** Aya AI Hackathon deployment

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework
- **Flask**: Python web framework serving as the main application server
- **SQLAlchemy**: ORM for database operations with declarative base models
- **Werkzeug ProxyFix**: Middleware for handling proxy headers in production environments

## Database Design
- **SQLite/PostgreSQL**: Flexible database configuration via environment variables
- **Models**: User management, wallet storage, transaction tracking, and portfolio management
- **Relationships**: Foreign key relationships between users, wallets, transactions, and portfolios
- **JSON Fields**: Metadata storage for transaction details and protocol-specific data

## Blockchain Integration
- **Multi-chain Support**: Dedicated client classes for Ethereum, Polygon, and Solana
- **Web3 Integration**: Web3.py for Ethereum-compatible chains with RPC connections
- **Solana Client**: Native Solana RPC client for SPL token operations
- **Wallet Management**: Encrypted private key storage with Fernet cryptography

## DeFi Operations
- **DEX Trading**: Token swaps via 1inch API and direct DEX protocol integration
- **Lending Protocols**: Aave and Compound integration for asset lending/borrowing
- **Yield Farming**: Liquidity provision to Uniswap, QuickSwap, and SushiSwap pools
- **Portfolio Management**: Real-time balance tracking and USD value calculation

## API Architecture
- **REST Endpoints**: Standard HTTP API with JSON responses
- **MCP Protocol**: JSON-RPC 2.0 server implementing Model Context Protocol
- **Authentication**: API key-based authentication with bearer token validation
- **Rate Limiting**: Request throttling and user session management

## Frontend Interface
- **Bootstrap**: Dark theme UI with responsive design
- **Chart.js**: Portfolio visualization and performance tracking
- **Feather Icons**: Consistent iconography throughout the interface
- **Real-time Updates**: WebSocket-ready architecture for live data feeds

## Security Architecture
- **API Key Management**: Prefixed keys with validation patterns
- **Wallet Encryption**: Private keys encrypted at rest using Fernet
- **Address Validation**: Blockchain-specific address format validation
- **Environment Configuration**: Sensitive data via environment variables

# External Dependencies

## Blockchain RPCs
- **Ethereum**: Infura or custom RPC endpoints for mainnet access
- **Polygon**: Public RPC endpoints for Polygon mainnet operations
- **Solana**: Official Solana RPC for mainnet-beta cluster

## DeFi APIs
- **1inch API**: DEX aggregation and optimal swap routing
- **Moralis API**: Token balance and portfolio data retrieval
- **CoinGecko API**: Real-time cryptocurrency pricing data

## Protocol Integrations
- **Uniswap V2/V3**: Direct smart contract interaction for swaps and liquidity
- **Aave**: Lending protocol integration for asset management
- **Compound**: Alternative lending protocol support
- **QuickSwap**: Polygon-based DEX operations
- **SushiSwap**: Multi-chain DEX protocol integration

## Development Tools
- **Web3.py**: Ethereum blockchain interaction library
- **Solana Python SDK**: Solana blockchain operations
- **Cryptography**: Wallet encryption and security utilities
- **Requests**: HTTP client for external API communication

## Frontend Libraries
- **Bootstrap**: UI component framework with dark theme
- **Chart.js**: Data visualization for portfolio analytics
- **Feather Icons**: SVG icon library for consistent UI elements