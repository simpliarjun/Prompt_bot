import { z } from 'zod';

// Mirrors backend GrievanceGenerateRequest
export const grievanceGenerateSchema = z.object({
  company_name: z.string().min(1, 'Company name is required').max(200),
  product_or_service: z.string().min(1, 'Product/service is required').max(200),
  category: z.enum([
    'product_defect', 'service_failure', 'billing_dispute',
    'delivery_issue', 'refund_request', 'warranty_claim',
    'data_privacy', 'other',
  ]),
  incident_date: z.string().min(1, 'Incident date is required'),
  order_reference: z.string().max(100).optional().or(z.literal('')),
  raw_description: z.string().min(10, 'Please describe your issue in at least 10 characters').max(4000),
  desired_resolution: z.enum([
    'refund', 'replacement', 'repair', 'apology',
    'compensation', 'contract_cancellation', 'other',
  ]),
  desired_resolution_details: z.string().max(500).optional().or(z.literal('')),
  contact_name: z.string().min(1, 'Your name is required').max(150),
  contact_email: z.string().email('Valid email required'),
  contact_phone: z.string().max(30).optional().or(z.literal('')),
});

export const loginSchema = z.object({
  email: z.string().email('Valid email required'),
  password: z.string().min(1, 'Password is required'),
});

export const registerSchema = z.object({
  full_name: z.string().min(1, 'Full name is required').max(150),
  email: z.string().email('Valid email required'),
  password: z.string().min(8, 'Password must be at least 8 characters').max(128),
});

export const CATEGORIES = [
  { value: 'product_defect', label: 'Product Defect' },
  { value: 'service_failure', label: 'Service Failure' },
  { value: 'billing_dispute', label: 'Billing Dispute' },
  { value: 'delivery_issue', label: 'Delivery Issue' },
  { value: 'refund_request', label: 'Refund Request' },
  { value: 'warranty_claim', label: 'Warranty Claim' },
  { value: 'data_privacy', label: 'Data / Privacy' },
  { value: 'other', label: 'Other' },
];

export const RESOLUTIONS = [
  { value: 'refund', label: 'Full Refund' },
  { value: 'replacement', label: 'Replacement' },
  { value: 'repair', label: 'Repair' },
  { value: 'apology', label: 'Formal Apology' },
  { value: 'compensation', label: 'Compensation' },
  { value: 'contract_cancellation', label: 'Contract Cancellation' },
  { value: 'other', label: 'Other' },
];
