# VPC for Lambda and RDS
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "orbital-parcel-ops-vpc"
  }
}

# Public subnets for NAT Gateway
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "orbital-parcel-ops-public-${count.index + 1}"
  }
}

# Private subnets for Lambda and RDS
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "orbital-parcel-ops-private-${count.index + 1}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "orbital-parcel-ops-igw"
  }
}

# NAT Gateway (costs $0.045/hour, ~$32/month)
# Commented out to stay in free tier - Lambda can still access RDS
# Uncomment only if Lambda needs internet access (external APIs)
# resource "aws_eip" "nat" {
#   domain = "vpc"
#
#   tags = {
#     Name = "orbital-parcel-ops-nat-eip"
#   }
# }
#
# resource "aws_nat_gateway" "main" {
#   allocation_id = aws_eip.nat.id
#   subnet_id     = aws_subnet.public[0].id
#
#   tags = {
#     Name = "orbital-parcel-ops-nat"
#   }
#
#   depends_on = [aws_internet_gateway.main]
# }

# Route tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "orbital-parcel-ops-public-rt"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  # Route to NAT Gateway commented out (saves $32/month)
  # Lambda can still access RDS within VPC
  # route {
  #   cidr_block     = "0.0.0.0/0"
  #   nat_gateway_id = aws_nat_gateway.main.id
  # }

  tags = {
    Name = "orbital-parcel-ops-private-rt"
  }
}

# Route table associations
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}
