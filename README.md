# Marketplace Shop

A full-stack online marketplace where users can buy and sell products. Built with React, Node.js, and Express.

## Features

- **User Authentication**: Register and login with JWT-based authentication
- **Product Management**: Create, view, update, and delete product listings
- **Shopping Cart**: Add products to cart and manage quantities
- **Order Management**: Place orders and track order status
- **User Dashboard**: Manage your products and view your orders
- **Search & Filter**: Search products and filter by category
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: React, React Router, Axios
- **Backend**: Node.js, Express
- **Authentication**: JWT (JSON Web Tokens)
- **Database**: JSON file-based storage (easily replaceable with MongoDB, PostgreSQL, etc.)

## Installation

1. Install dependencies for both server and client:
```bash
npm run install-all
```

Or install separately:
```bash
# Install server dependencies
npm install

# Install client dependencies
cd client
npm install
cd ..
```

2. Create a `.env` file in the root directory:
```
PORT=5000
JWT_SECRET=your-secret-key-change-in-production
```

## Running the Application

### Development Mode

Run both server and client concurrently:
```bash
npm run dev
```

Or run separately:
```bash
# Terminal 1 - Start server
npm run server

# Terminal 2 - Start client
npm run client
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Production Build

1. Build the React app:
```bash
npm run build
```

2. Start the server:
```bash
npm run server
```

The server will serve the built React app and API on port 5000.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (protected)

### Products
- `GET /api/products` - Get all products
- `GET /api/products/:id` - Get single product
- `GET /api/products/seller/:sellerId` - Get products by seller
- `POST /api/products` - Create product (protected)
- `PUT /api/products/:id` - Update product (protected)
- `DELETE /api/products/:id` - Delete product (protected)

### Cart
- `GET /api/cart` - Get user's cart (protected)
- `POST /api/cart/add` - Add item to cart (protected)
- `PUT /api/cart/update` - Update cart item quantity (protected)
- `DELETE /api/cart/remove/:productId` - Remove item from cart (protected)
- `DELETE /api/cart/clear` - Clear cart (protected)

### Orders
- `GET /api/orders` - Get user's orders (protected)
- `GET /api/orders/seller` - Get seller's orders (protected)
- `POST /api/orders/create` - Create order from cart (protected)
- `PUT /api/orders/:id/status` - Update order status (protected)

## Project Structure

```
marketplace-shop/
├── client/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── context/       # React context (Auth)
│   │   ├── pages/         # Page components
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── server/                 # Express backend
│   ├── routes/            # API routes
│   ├── utils/             # Database utilities
│   └── index.js           # Server entry point
├── data/                  # JSON database files (auto-created)
├── package.json
└── README.md
```

## Usage

1. **Register/Login**: Create an account or login to start using the marketplace
2. **Browse Products**: View all available products on the Products page
3. **Add Products**: Go to Dashboard to add your own products for sale
4. **Shopping**: Add products to cart and proceed to checkout
5. **Manage Orders**: View and track your orders in the Orders page

## Notes

- The application uses JSON files for data storage. For production, consider migrating to a proper database (MongoDB, PostgreSQL, etc.)
- JWT tokens are stored in localStorage. For enhanced security, consider using httpOnly cookies
- Image URLs are currently stored as strings. For production, implement proper image upload functionality
- Payment processing is simulated. Integrate a payment gateway (Stripe, PayPal, etc.) for real transactions

## License

ISC
