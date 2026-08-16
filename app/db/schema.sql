-- =====================================================
-- ESTATE AI ASSISTANT DATABASE
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

--------------------------------------------------------
-- Properties
--------------------------------------------------------

CREATE TABLE IF NOT EXISTS properties (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    listing_id TEXT UNIQUE NOT NULL,

    title TEXT NOT NULL,

    description TEXT,

    price NUMERIC(12,2),

    currency TEXT DEFAULT 'GBP',

    property_type TEXT,

    listing_type TEXT,

    status TEXT,

    bedrooms INTEGER,

    bathrooms INTEGER,

    address TEXT,

    city TEXT,

    postcode TEXT,

    parking BOOLEAN DEFAULT FALSE,

    garden BOOLEAN DEFAULT FALSE,

    garage BOOLEAN DEFAULT FALSE,

    epc_rating TEXT,

    listing_url TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------
-- Buyer Leads
--------------------------------------------------------

CREATE TABLE IF NOT EXISTS buyer_leads (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    name TEXT,

    email TEXT,

    phone TEXT,

    status TEXT DEFAULT 'New',

    budget_min NUMERIC,

    budget_max NUMERIC,

    preferred_locations TEXT[],

    property_type TEXT,

    bedrooms INTEGER,

    bathrooms INTEGER,

    parking_required BOOLEAN,

    garden_required BOOLEAN,

    mortgage_status TEXT,

    deposit_percentage INTEGER,

    first_time_buyer BOOLEAN,

    chain_status TEXT,

    moving_timeline TEXT,

    selected_property_id UUID REFERENCES properties(id),

    selected_property_url TEXT,

    summary_text TEXT,

    summary_json JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------
-- Seller Leads
--------------------------------------------------------

CREATE TABLE IF NOT EXISTS seller_leads (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    name TEXT,

    email TEXT,

    phone TEXT,

    property_address TEXT,

    property_type TEXT,

    bedrooms INTEGER,

    bathrooms INTEGER,

    estimated_value NUMERIC,

    reason_for_selling TEXT,

    selling_timeline TEXT,

    occupied BOOLEAN,

    valuation_required BOOLEAN DEFAULT TRUE,

    preferred_contact_time TEXT,

    summary_text TEXT,

    summary_json JSONB,

    status TEXT DEFAULT 'New',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------
-- Viewings
--------------------------------------------------------

CREATE TABLE IF NOT EXISTS viewings (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    buyer_lead_id UUID REFERENCES buyer_leads(id),

    property_id UUID REFERENCES properties(id),

    viewing_date DATE,

    viewing_time TIME,

    status TEXT DEFAULT 'Booked',

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------
-- Valuations
--------------------------------------------------------

CREATE TABLE IF NOT EXISTS valuations (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    seller_lead_id UUID REFERENCES seller_leads(id),

    valuation_date DATE,

    valuation_time TIME,

    status TEXT DEFAULT 'Booked',

    notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------
-- Conversation Sessions
--------------------------------------------------------

CREATE TABLE IF NOT EXISTS conversation_sessions (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    lead_type TEXT,

    lead_id UUID,

    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    ended_at TIMESTAMP,

    completed BOOLEAN DEFAULT FALSE,

    status TEXT DEFAULT 'ACTIVE',

    phone_number TEXT,

    summary TEXT,

    analysis JSONB,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------
-- Conversation Messages
--------------------------------------------------------

CREATE TABLE IF NOT EXISTS conversation_messages (

    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    session_id UUID REFERENCES conversation_sessions(id) ON DELETE CASCADE,

    speaker TEXT,

    message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);