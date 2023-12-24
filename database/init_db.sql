-- Creating the Customers Table
CREATE TABLE Customers (
    CustomerID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE,
    Phone VARCHAR(15),
    Address VARCHAR(255),
    City VARCHAR(50),
    Country VARCHAR(50),
    RegistrationDate TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Creating the Suppliers Table
CREATE TABLE Suppliers (
    SupplierID SERIAL PRIMARY KEY,
    SupplierName VARCHAR(100) NOT NULL,
    ContactName VARCHAR(100),
    Address VARCHAR(255),
    City VARCHAR(50),
    Country VARCHAR(50),
    Phone VARCHAR(15),
    Email VARCHAR(100) UNIQUE
);

-- Creating the Categories Table
CREATE TABLE Categories (
    CategoryID SERIAL PRIMARY KEY,
    CategoryName VARCHAR(50) NOT NULL,
    Description TEXT
);

-- Creating the Products Table
CREATE TABLE Products (
    ProductID SERIAL PRIMARY KEY,
    ProductName VARCHAR(100) NOT NULL,
    SupplierID INT,
    CategoryID INT,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    Description TEXT,
    StockQuantity INT NOT NULL DEFAULT 0,
    FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID)
);

-- Creating the Orders Table
CREATE TABLE Orders (
    OrderID SERIAL PRIMARY KEY,
    CustomerID INT,
    OrderDate TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10, 2) NOT NULL,
    ShippingAddress VARCHAR(255),
    OrderStatus VARCHAR(50) DEFAULT 'Processing',
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Creating the OrderDetails Table
CREATE TABLE OrderDetails (
    OrderDetailID SERIAL PRIMARY KEY,
    OrderID INT,
    ProductID INT,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- Creating the Payments Table
CREATE TABLE Payments (
    PaymentID SERIAL PRIMARY KEY,
    OrderID INT,
    PaymentDate TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Amount DECIMAL(10, 2) NOT NULL,
    PaymentMethod VARCHAR(50),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);

-- Creating the CustomerFeedback Table
CREATE TABLE CustomerFeedback (
    FeedbackID SERIAL PRIMARY KEY,
    CustomerID INT,
    ProductID INT,
    Rating INT CHECK (Rating BETWEEN 1 AND 5),
    Comment TEXT,
    FeedbackDate TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);


-- Inserting data into the Customers table
INSERT INTO Customers (FirstName, LastName, Email, Phone, Address, City, Country) VALUES
('John', 'Doe', 'johndoe@example.com', '1234567890', '123 Main St', 'New York', 'USA'),
('Jane', 'Smith', 'janesmith@example.com', '0987654321', '456 Oak St', 'Los Angeles', 'USA'),
('Alice', 'Johnson', 'alicejohnson@example.com', '5555555555', '789 Pine St', 'Chicago', 'USA');

-- Inserting data into the Suppliers table
INSERT INTO Suppliers (SupplierName, ContactName, Address, City, Country, Phone, Email) VALUES
('Global Supplies', 'Sam Wilson', '100 Industrial Way', 'San Francisco', 'USA', '1112223333', 'contact@globalsupplies.com'),
('Quality Goods Inc.', 'Rita Patel', '200 Market St', 'Boston', 'USA', '4445556666', 'info@qualitygoods.com');

-- Inserting data into the Categories table
INSERT INTO Categories (CategoryName, Description) VALUES
('Electronics', 'Devices and gadgets'),
('Clothing', 'Apparel and accessories'),
('Home & Garden', 'Furniture and home decor');

-- Inserting data into the Products table
INSERT INTO Products (ProductName, SupplierID, CategoryID, UnitPrice, Description, StockQuantity) VALUES
('Smartphone', 1, 1, 299.99, 'Latest model smartphone with high-end features', 50),
('T-Shirt', 2, 2, 19.99, 'Cotton t-shirt in various sizes and colors', 100),
('Coffee Table', 2, 3, 89.99, 'Modern wooden coffee table', 30);

-- Inserting data into the Orders table
INSERT INTO Orders (CustomerID, OrderDate, TotalAmount, ShippingAddress, OrderStatus) VALUES
(1, '2023-12-01 10:00:00', 319.98, '123 Main St, New York, USA', 'Shipped'),
(2, '2023-12-02 15:30:00', 109.98, '456 Oak St, Los Angeles, USA', 'Processing');

-- Inserting data into the OrderDetails table
INSERT INTO OrderDetails (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 1, 299.99),
(2, 2, 2, 19.99);

-- Inserting data into the Payments table
INSERT INTO Payments (OrderID, PaymentDate, Amount, PaymentMethod) VALUES
(1, '2023-12-01 10:05:00', 319.98, 'Credit Card'),
(2, '2023-12-02 15:35:00', 109.98, 'PayPal');

-- Inserting data into the CustomerFeedback table
INSERT INTO CustomerFeedback (CustomerID, ProductID, Rating, Comment) VALUES
(1, 1, 4, 'Great product, but battery life could be better'),
(2, 2, 5, 'Love the t-shirts, very comfortable');
