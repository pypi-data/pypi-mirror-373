#!/usr/bin/env python3
"""
Example usage of SimpleSpec package.
"""

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from simplespec import generate_simple_spec


class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


@dataclass
class Location:
    latitude: float
    longitude: float


class Address(BaseModel):
    street: str = Field(min_length=1, max_length=100, description="Street address")
    city: str = Field(min_length=1, max_length=50, description="City name")
    country: str = Field(default="US", description="Country code")
    location: Location | None = None


class User(BaseModel):
    """A user in the system."""

    name: str = Field(min_length=1, max_length=100, description="Full name")
    email: str = Field(description="Email address")
    age: int = Field(ge=18, le=120, description="Age in years")
    status: Status = Field(default=Status.ACTIVE, description="User status")
    address: Address | None = None
    tags: list[str] = Field(default_factory=list, description="User tags")


def main():
    """Demonstrate SimpleSpec functionality."""
    print("SimpleSpec Example")
    print("=" * 50)

    # Generate spec for the User model
    spec = generate_simple_spec(User, max_depth=10)
    print(spec)

    print("\n" + "=" * 50)
    print("Programmatic access:")
    print(f"Root type: {spec.self.type}")
    print(f"Root description: {spec.self.description}")
    print(f"Number of referenced types: {len(spec.refs)}")

    print("\nReferenced types:")
    for ref in spec.refs:
        print(f"- {ref.type}: {len(ref.properties)} properties")

    print("\nUser properties:")
    for prop_name, prop in spec.self.properties.items():
        print(f"- {prop_name}: {prop.type}")
        if prop.description:
            print(f"  Description: {prop.description}")


if __name__ == "__main__":
    main()
